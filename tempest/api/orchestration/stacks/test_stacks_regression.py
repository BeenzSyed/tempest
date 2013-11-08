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

    @attr(type='smoke')
    def _test_stack(self, template):
        env = "staging"
        template_giturl = "https://raw.github.com/heat-ci/heat-templates/master/" + env + "/" + template + ".template"
        print template_giturl

        response_templates = requests.get(template_giturl, timeout=3)
        yaml_template = yaml.safe_load(response_templates.content)

        stack_name = rand_name(template)

        if 'key_name' in yaml_template['parameters']:
            parameters = {
            'key_name': "sabeen"
            }
            # parameters = {
            # 'key_name': "sabeen",
            # 'git_url': "https://github.com/timductive/phphelloworld"
            # }
        if 'git_url' in yaml_template['parameters']:
            parameters['git_url'] = "https://github.com/timductive/phphelloworld"
        else:
            parameters = {}

        # parameters = {
        # #     'InstanceType': self.orchestration_cfg.instance_type,
        # #     'ImageId': self.orchestration_cfg.image_ref,
        #     'key_name': "sabeen"
        #     }
        #pdb.set_trace()
        stack_identifier = self.create_stack(stack_name, yaml_template, parameters)
        #print stack_identifier
        stack_id = stack_identifier.split('/')[1]
        #pdb.set_trace()
        count = 0
        resp, body = self.get_stack(stack_id)
        #print "response is: %s" % resp
        print "stack status is: %s ,%s" % (body['stack_status'], body['stack_status_reason'])

        while body['stack_status'] == 'CREATE_IN_PROGRESS' and count < 90:
            resp, body = self.get_stack(stack_id)
            print "Deployment in %s status. Checking again in 1 minute" % body['stack_status']
            time.sleep(60)
            count += 1
            if body['stack_status'] == 'CREATE_FAILED':
                print "Stack create failed. Here's why: %s" % body['stack_status_reason']

        if body['stack_status'] == 'CREATE_COMPLETE':
            print "The deployment took %s minutes" % count

        # wait for create complete (with no resources it should be instant)
        # timetaken = self.client.wait_for_stack_status(stack_identifier, 'CREATE_COMPLETE')
        # print "time taken for stack to deploy: %s" %timetaken
        # stack count will increment by 1
        resp, stacks = self.client.list_stacks()
        list_ids = list([stack['id'] for stack in stacks])
        self.assertIn(stack_id, list_ids)
        print resp

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
