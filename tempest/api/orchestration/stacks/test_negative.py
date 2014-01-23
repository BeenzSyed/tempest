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
from tempest.clients import OrchestrationManager
from tempest.openstack.common import log as logging
from tempest.common.utils.data_utils import rand_name

import requests
import yaml


LOG = logging.getLogger(__name__)


class StacksTestJSON(base_multipleusers.BaseMultipleOrchestrationTest):
    _interface = 'json'

    empty_template = "HeatTemplateFormatVersion: '2013-05-23'\n"

    @classmethod
    def setUpClass(cls):
        super(StacksTestJSON, cls).setUpClass()

    def test_verify_stack_against_different_user(self):
        user_first = self.managers[0]
        user_second = self.managers[1]
        stack_identifier = self._create_stack(user_first)
        stack_id = stack_identifier.split('/')[1]
        stack_name = stack_identifier.split('/')[0]
        try:
            resp , body = self.get_stack(user_second, stack_id)
        except Exception as e:
                failure_msg = repr(e)
                resp, body = self.delete_stack(user_first, stack_name, stack_id)
        print failure_msg
        print "StackNotFound: The Stack (%s) could not be found." % stack_id

    def test_verify_username_pwd(self):
        manager = OrchestrationManager(username="heatqe",
                                       password="wrongpwd",
                                       tenant_name="862456")
        try:
            self._create_stack(manager)
        except Exception as e:
            failure_msg = repr(e)
        print "test"
        print e, failure_msg

    def _create_stack(self, manager):
        template = "php-app"
        region = "DFW"
        env = "staging"
        template_git_url = "https://raw.github" \
                           ".com/heat-ci/heat-templates/master/%s/%s.template" \
                           % (env, template)
        response_templates = requests.get(template_git_url, timeout=3)
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
        stack_identifier = self.create_stack(manager, stack_name, region,
                                             yaml_template,
                                             parameters)
        print stack_identifier
        stack_id = stack_identifier.split('/')[1]
        self.get_stack(manager, stack_id)
        return stack_identifier

    def test_get_api_version(self):
        user = self.managers[0]
        regions = ['DFW', 'ORD', 'IAD', 'SYD', 'HKG']
        for region in regions:
            resp, body = self.get_api_version(user, region)
            body = body['versions']
            versions = map(lambda x: x['id'], body)
            self.assertEquals(1, len(versions))
            self.assertEquals("v1.0", versions[0])
