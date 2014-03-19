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
import time
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

    def test_devstack_realDeployment(self):
        self._test_stack("devstack")

    def test_dotnetnuke_realDeployment(self):
        self._test_stack("dotnetnuke")

    def test_mongodb_realDeployment(self):
        self._test_stack("mongodb")

    def test_mysql_realDeployment(self):
        self._test_stack("mysql")

    def test_php_app_realDeployment(self):
        self._test_stack("php-app")

    def test_rcbops_realDeployment(self):
        self._test_stack("rcbops_allinone_inone")

    def test_redis_realDeployment(self):
        self._test_stack("redis")

    def test_repose_realDeployment(self):
        self._test_stack("repose")

    def test_ruby_on_rails_realDeployment(self):
        self._test_stack("ruby-on-rails")

    def test_wordpress_multi_realDeployment(self):
        self._test_stack("wordpress-multi")

    def test_wordpress_multi_windows_realDeployment(self):
        self._test_stack("wordpress-multinode-windows")

    def test_wordpress_single_winserver_realDeployment(self):
        self._test_stack("wordpress-single-winserver")

    def test_wordpress_winserver_clouddb_realDeployment(self):
        self._test_stack("wordpress-winserver-clouddb")

    def test_wp_resource_realDeployment(self):
        self._test_stack("wp-resource")

    def test_wp_single_linux_realDeployment(self):
        self._test_stack("wp-single-linux-cdb")

    def test_rackconnect_realDeployment(self):
        self._test_stack("php-app")

    def test_wordpress_multi_dns_realDeployment(self):
        self._test_stack("wordpress-multi-dns")

    def test_ubuntu(self):
        self._test_stack("hello-world", "ubuntu")

    def test_centos(self):
        self._test_stack("hello-world", "centos")

    @attr(type='smoke')
    def _test_stack(self, template, image=None):
        print os.environ.get('TEMPEST_CONFIG')

        env = self.config.orchestration['env']

        #templates on github
        #template_giturl = "https://raw2.github.com/heat-ci/heat-templates/master/" + env + "/" + template + ".template"
        template_giturl = "https://raw.githubusercontent.com/rackspace-orchestration-templates/heat-ci/master/" + env + "/" + template + ".template"
        response_templates = requests.get(template_giturl, timeout=3)
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
                    parameters['domain_record_type']= domain_record_type
            if 'domain_name' in yaml_template['parameters']:
                    parameters['domain_name'] = domain_name

            if 'git_url' in yaml_template['parameters']:
                parameters['git_url'] = "https://github.com/timductive/phphelloworld"
            if 'image_id' in yaml_template['parameters'] and image=="ubuntu":
                parameters['image_id'] = "80fbcb55-b206-41f9-9bc2-2dd7aac6c061"
            if 'image_id' in yaml_template['parameters'] and image=="centos":
                parameters['image_id'] = "ea8fdf8a-c0e4-4a1f-b17f-f5a421cda051"

            print "\nDeploying %s in %s" % (template, region)
            #pdb.set_trace()
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
