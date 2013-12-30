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

from tempest.api.orchestration import base_multipleusers
from tempest.common.utils.data_utils import rand_name
from tempest.openstack.common import log as logging
from tempest.test import attr
import requests
import yaml
import time
import os
import pdb

LOG = logging.getLogger(__name__)


class StacksTestJSON(base_multipleusers.BaseMultipleOrchestrationTest):
    _interface = 'json'

    empty_template = "HeatTemplateFormatVersion: '2013-05-23'\n"

    @classmethod
    def setUpClass(cls):
        super(StacksTestJSON, cls).setUpClass()



    def test_rackconnect_realDeployment(self):
        self._test_stack_for_RackConnect("php-app")

    def _send_deploy_time_graphite(self, region, template, deploy_time, buildfail):
        cmd = 'echo "heat.qa.build-tests.' + region + '.' + template \
              + '.' + buildfail + '  ' + str(deploy_time) \
              + ' `date +%s`" | ' \
                'nc http://graphite.staging.rs-heat.com/ ' \
                '2003 -q 2'
        print cmd
        os.system(cmd)
        print "Deploy time sent to graphite"

    def _test_stack_for_RackConnect(self, template):
        user_rackconnect = self.managers[2]
        env = "staging"
        region = "DFW"
        template_giturl = "https://raw.github.com/heat-ci/heat-templates/master/" + env + "/" + template + ".template"
        response_templates = requests.get(template_giturl, timeout=3)
        yaml_template = yaml.safe_load(response_templates.content)
        stack_name = rand_name("sabeen"+template)
        parameters = {}
        if 'key_name' in yaml_template['parameters']:
            parameters = {
                    'key_name': 'sabeen'
                }
            if 'git_url' in yaml_template['parameters']:
                parameters['git_url'] = "https://github.com/timductive/phphelloworld"

            print "\nDeploying %s in %s" % (template,region)
            stack_identifier = self.create_stack(user_rackconnect,stack_name, region,
                                             yaml_template, parameters)
            #stack_identifier = self.create_stack(stack_name, region,
            # yaml_template, parameters)
            stack_id = stack_identifier.split('/')[1]
            count = 0
            resp, body = self.get_stack(user_rackconnect,stack_id)
            print "Stack %s status is: %s, %s" % (stack_name, body['stack_status'], body['stack_status_reason'])

            while body['stack_status'] == 'DEPLOYING' and count < 90:
                resp, body = self.get_stack(user_rackconnect,stack_id)
                if resp['status'] != '200':
                    print "The response is: %s" % resp
                    self.fail(resp)
                print "Deployment in %s status. Checking again in 1 minute" % body['stack_status']
                time.sleep(60)
                count += 1
                if body['stack_status'] == 'FAILED':
                    print "Stack create failed. Here's why: %s" % body['stack_status_reason']
                    print "Deleting the stack now"
                    resp, body = self.delete_stack(user_rackconnect,
                                                   stack_name, stack_id)
                    if resp['status'] != '204':
                        print "Delete did not work"
                    self._send_deploy_time_graphite(region, template, count, "failtime")
                    self.fail("Stack create failed")
                if count == 90:
                    print "Stack create has taken over 90 minutes. Force failing now."
                    self._send_deploy_time_graphite(region, template, count, "failtime")
                    resp, body = self.delete_stack(stack_name, stack_id)
                    if resp['status'] != '204':
                        print "Delete did not work"
                    self.fail("Stack create took too long")

            if body['stack_status'] == 'DEPLOYED':
                print "The deployment took %s minutes" % count
                self._send_deploy_time_graphite(region, template, count, "buildtime")
                #extract region and name of template

                #delete stack
                print "Deleting stack now"
                resp, body = self.delete_stack(user_rackconnect,stack_name,
                                               stack_id)
                if resp['status'] != '204':
                    print "Delete did not work"

            else:
                print "Something went wrong! This could be the reason: %s" % body['stack_status_reason']
