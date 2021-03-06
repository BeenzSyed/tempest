# vim: tabstop=4 shiftwidth=4 softtabstop=4

#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from tempest.api.orchestration import base
from tempest.common.utils.data_utils import rand_name
from tempest.openstack.common import log as logging
from datetime import datetime
from tempest.test import attr
import requests
import yaml
from testconfig import config
import os
import pdb


LOG = logging.getLogger(__name__)


class StacksTestJSON(base.BaseOrchestrationTest):
    _interface = 'json'

    empty_template = "HeatTemplateFormatVersion: '2013-05-23'\n"

    @classmethod
    def setUpClass(cls):
        super(StacksTestJSON, cls).setUpClass()
        cls.client = cls.orchestration_client

    def test_all(self):
        self._test_stack()

    @attr(type='smoke')
    def _test_stack(self, template=None, image=None):
        print os.environ.get('TEMPEST_CONFIG')

        print os.environ.get('TEMPEST_CONFIG')
        if os.environ.get('TEMPEST_CONFIG') == None:
            print "Set the environment varible TEMPEST_CONFIG to a config file."
            self.fail("Environment variable is not set.")

        env = self.config.orchestration['env']
        account = self.config.identity['username']

        if template == None:
            template_giturl = config['template_url']
            template = template_giturl.split("/")[-1].split(".")[0]
            print "template is %s" % template
        else:
            template_giturl = "https://raw.githubusercontent.com/heat-ci/heat-templates/master/"+env+"/"+template+".template"

        response_templates = requests.get(template_giturl, timeout=10)
        if response_templates.status_code != requests.codes.ok:
            print "This template does not exist: %s" % template_giturl
            self.fail("The template does not exist.")
        else:
            yaml_template = yaml.safe_load(response_templates.content)

        regionsConfig = self.config.orchestration['regions']
        regions = regionsConfig.split(",")
        for region in regions:
            stack_name = rand_name("qe_"+template+region)
            domain_name = "example%s.com" %datetime.now().microsecond
            email_address = "heattest@rs.com"
            domain_record_type = "A"

            parameters = {}
            if 'key_name' in yaml_template['parameters']:
                parameters = {
                    'key_name': 'sabeen'
                }
            #     parameters = {}
            if 'key_name' in yaml_template['parameters']:
                  parameters['key_name'] = 'sabeen'
            if 'email_address' in yaml_template['parameters']:
                    parameters['email_address'] = email_address
            if 'domain_record_type' in yaml_template['parameters']:
                    parameters['domain_record_type'] = domain_record_type
            if 'domain_name' in yaml_template['parameters']:
                    parameters['domain_name'] = domain_name

            if 'git_url' in yaml_template['parameters']:
                parameters['git_url'] = "https://github.com/timductive/phphelloworld"
            if 'image_id' in yaml_template['parameters'] and image=="ubuntu":
                parameters['image_id'] = "80fbcb55-b206-41f9-9bc2-2dd7aac6c061"
            if 'image_id' in yaml_template['parameters'] and image=="centos":
                parameters['image_id'] = "ea8fdf8a-c0e4-4a1f-b17f-f5a421cda051"

            print "\nDeploying %s in %s" % (template, region)
            csresp, csbody, stack_identifier = self.create_stack(stack_name, region, yaml_template, parameters)
            print csresp
            print csbody
            print stack_identifier

            if stack_identifier == 0:
                print "Stack create failed. Here's why: %s, %s" % (csresp, csbody)
                self.fail("Stack build failed.")
            else:
                stack_id = stack_identifier.split('/')[1]

                #delete stack
                print "Deleting stack now"
                resp, body = self.delete_stack(stack_name, stack_id, region)
                print resp
                print body
                if resp['status'] != '204':
                    print "Delete did not work"
                    self.fail("Delete did not work: %s %s" %(resp, body))
                else:
                    print "Deleted!"
