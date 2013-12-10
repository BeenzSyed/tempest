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
from tempest.openstack.common import log as logging
from tempest.performance import load_pattern
from tempest.common.utils.data_utils import rand_name
from tempest.performance.load_test_runner import LoadTestRunner

import requests
import yaml
import datetime
import time
import multimechanize


LOG = logging.getLogger(__name__)


class StacksTestJSON(base.BaseOrchestrationTest):
    _interface = 'json'

    empty_template = "HeatTemplateFormatVersion: '2013-05-23'\n"

    @classmethod
    def setUpClass(cls):
        super(StacksTestJSON, cls).setUpClass()
        cls.client = cls.orchestration_client


    def test_create_delete_limit(self):
        pass

    def test_getstack_limit(self):
        #limit 200/min
        pattern = load_pattern.StepLoad(5, 200, 10, 15)
        runner = LoadTestRunner(pattern)
        runner.run(self._create_stack)
        pattern = load_pattern.StepLoad(15, 200, 10, 15)
        runner = LoadTestRunner(pattern)
        runner.run(self._get_stack)

    def test_deletestack_limit(self):
        #limit 100/min
        pattern = load_pattern.StepLoad(5, 100, 10, 15)
        runner = LoadTestRunner(pattern)
        runner.run(self._create_stack)
        pattern = load_pattern.StepLoad(5, 100, 10, 15)
        runner = LoadTestRunner(pattern)
        runner.run(self._delete_stack)

    def test_updatestack_limit(self):
        #limit 20/min
        pattern = load_pattern.StepLoad(2, 20, 2, 2)
        runner = LoadTestRunner(pattern)
        runner.run(self._create_stack)

    def test_createstack_limit(self):
        #limit 20/min
        pattern = load_pattern.StepLoad(2, 20, 2, 2)
        runner = LoadTestRunner(pattern)
        runner.run(self._create_stack)

    def _get_stack(self):
        # GET limit 200/min
        resp, stacks = self.client.list_stacks()
        list_ids = list([stack['id'] for stack in stacks])
        print list_ids
        print datetime.datetime.now()

    def _delete_stack(self):
        # Delete call will need force delete method to be implemented first
        #limit is 100/min
        resp, stacks = self.client.list_stacks()
        for stack in stacks:
            stack_id = stack['id']
            stack_name = stack['stack_name']
            resp = self.client.delete_stack(stack_name, stack_id)
            print resp
        print datetime.datetime.now()

    def _update_stack(self):
        # To update the stack PUT request
        # Limit set 20/min
        for i in range(100):
            resp, stacks = self.client.list_stacks()
            for stack in stacks:
                stack_name = stack['stack_name']
                stack_id = stack['id']
                resp, stack = self.client.update_stack(stack_id,stack_name)
                print resp
            print datetime.datetime.now()

    def _create_stack(self):
        template = "php-app"
        region = "DFW"
        env = "staging"
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

        print "\nDeploying %s in %s" % (template, region)
        stack_identifier = self.create_stack(stack_name, region, yaml_template, parameters)
        print stack_identifier
        stack_id = stack_identifier.split('/')[1]
        resp, body = self.get_stack(stack_id)
        print "Stack %s status is: %s, %s" % (stack_name,
        body['stack_status'], body['stack_status_reason'])
        print datetime.datetime.now()


