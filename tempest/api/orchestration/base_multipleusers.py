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

import tempest.test
from tempest import clients
from tempest.openstack.common import log as logging

LOG = logging.getLogger(__name__)


class BaseMultipleOrchestrationTest(tempest.test.BaseTestCase):
    """Base test case class for all Orchestration API
       tests with multiple users.
    ."""

    @classmethod
    def setUpClass(cls):
        cls.managers = []
        super(BaseMultipleOrchestrationTest, cls).setUpClass()
        users = [
            {
                "username": "heatqe",
                "password": "Longhorn786!",
                "tenant_id": "862456"
            },
            {
                "username": "heatdev",
                "password": "pHxA5rJQ",
                "tenant_id": "836933"
            }
        ]
        for user in users:
            cls.managers.append(
                clients.OrchestrationManager(user["username"],
                                             user["password"],
                                             user["tenant_id"]))
        cls.stacks = []

    @classmethod
    def create_stack(cls, manager, stack_name, region, template_data,
                     parameters={}):

        resp, body = manager.orchestration_client.create_stack(
            stack_name,
            region,
            template=template_data,
            parameters=parameters)
        stack_id = resp['location'].split('/')[-1]
        stack_identifier = '%s/%s' % (stack_name, stack_id)
        cls.stacks.append({
            'client': manager.orchestration_client,
            'stack_id': stack_identifier
        })
        return stack_identifier

    @classmethod
    def get_stack(cls, manager, stack_id):
        """Returns the details of a single stack."""
        resp, body = manager.orchestration_client.get_stack(stack_id)

        return resp, body['stack']

    @classmethod
    def delete_stack(cls, manager, stack_name, stack_id):
        resp, body = manager.orchestration_client.delete_stack(stack_name,
                                                               stack_id)
        return resp, body

    @classmethod
    def clear_stacks(cls):
        for stack_info in cls.stacks:
            try:
                stack_info['client'].delete_stack(stack_info['stack_id'])
            except Exception:
                pass

        for stack_info in cls.stacks:
            try:
                stack_info['client'].wait_for_stack_status(
                    stack_info['stack_id'], 'DELETE_COMPLETE')
            except Exception:
                pass

    @classmethod
    def tearDownClass(cls):
        cls.clear_stacks()
        super(BaseMultipleOrchestrationTest, cls).tearDownClass()
