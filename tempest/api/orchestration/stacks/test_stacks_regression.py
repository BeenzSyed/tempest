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

    @attr(type='smoke')
    def _test_stack(self, template):
        env = "prod"
        template_giturl = "https://raw.github.com/heat-ci/heat-templates/master/" + env + "/" + template + ".template"
        #print template_giturl
        response_templates = requests.get(template_giturl, timeout=3)
        yaml_template = yaml.safe_load(response_templates.content)

        #pf is the variable that stays 0 if no failures occur, turns to 1 if a build fails
        pf = 0

        regions = ['DFW', 'ORD', 'IAD', 'SYD', 'HKG']
        for region in regions:
            stack_name = rand_name("prod_regr"+template)
            parameters = {}
            if 'key_name' in yaml_template['parameters']:
                #parameters['key_name'] = "sabeen"
                parameters = {
                    'key_name': 'sabeen'
                }
            if 'git_url' in yaml_template['parameters']:
                parameters['git_url'] = "https://github.com/timductive/phphelloworld"

            print "\nDeploying %s in %s" % (template, region)
            stack_identifier = self.create_stack(stack_name, region, yaml_template, parameters)
            stack_id = stack_identifier.split('/')[1]
            count = 0
            resp, body = self.get_stack(stack_id)
            print "Stack %s status is: %s, %s" % (stack_name, body['stack_status'], body['stack_status_reason'])

            while body['stack_status'] == 'CREATE_IN_PROGRESS' and count < 90:
                resp, body = self.get_stack(stack_id)
                if resp['status'] != '200':
                    print "The response is: %s" % resp
                    self.fail(resp)
                print "Deployment in %s status. Checking again in 1 minute" % body['stack_status']
                time.sleep(60)
                count += 1
                if body['stack_status'] == 'CREATE_FAILED':
                    print "Stack create failed. Here's why: %s" % body['stack_status_reason']
                    self._send_deploy_time_graphite(region, template, count, "failtime")
                    print "Deleting the stack now"
                    resp, body = self.delete_stack(stack_name, stack_id)
                    if resp['status'] != '204':
                        print "Delete did not work"
                    pf += 1
                elif count == 90:
                    print "Stack create has taken over 90 minutes. Force failing now."
                    self._send_deploy_time_graphite(region, template, count, "failtime")
                    print "Stack create took too long. Deleting stack now."
                    resp, body = self.delete_stack(stack_name, stack_id)
                    if resp['status'] != '204':
                        print "Delete did not work"
                    pf += 1

            if body['stack_status'] == 'CREATE_COMPLETE':
                print "The deployment took %s minutes" % count
                self._send_deploy_time_graphite(region, template, count, "buildtime")
                #extract region and name of template
                #delete stack
                print "Deleting stack now"
                resp, body = self.delete_stack(stack_name, stack_id)
                if resp['status'] != '204':
                    print "Delete did not work"

            else:
                print "Something went wrong! This could be the reason: %s" % body['stack_status_reason']

        if pf > 0:
            self.fail("Stack build failed.")


        # wait for create complete (with no resources it should be instant)
        # timetaken = self.client.wait_for_stack_status(stack_identifier, 'CREATE_COMPLETE')
        # print "time taken for stack to deploy: %s" %timetaken
        # stack count will increment by 1
        # resp, stacks = self.client.list_stacks()
        # list_ids = list([stack['id'] for stack in stacks])
        # self.assertIn(stack_id, list_ids)
        # print resp

        # # fetch the stack
        # resp, stack = self.client.get_stack(stack_identifier)
        # self.assertEqual('CREATE_COMPLETE', stack['stack_status'])
        #
        # # fetch the stack by name
        # resp, stack = self.client.get_stack(stack_name)
        # self.assertEqual('CREATE_COMPLETE', stack['stack_status'])
        #
        # # fetch the stack by id
        # resp, stack = self.client.get_stack(stack_id)
        # self.assertEqual('CREATE_COMPLETE', stack['stack_status'])

        # delete the stack
        #resp = self.client.delete_stack(stack_identifier)
        #self.assertEqual('204', resp[0]['status'])

    def _send_deploy_time_graphite(self, region, template, deploy_time, buildfail):
        cmd = 'echo "heat.qa.build-tests.' + region + '.' + template \
              + '.' + buildfail + '  ' + str(deploy_time) \
              + ' `date +%s`" | ' \
                'nc http://graphite.staging.rs-heat.com/ ' \
                '2003 -q 2'
        print cmd
        os.system(cmd)
        print "Deploy time sent to graphite"
