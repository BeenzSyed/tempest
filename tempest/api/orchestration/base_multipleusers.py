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
import json
import datetime
import pdb

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
            },
            {
                "username": "rctestsyd02",
                "password": "Hybr1d99",
                "tenant_id": "828222"
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
        #pdb.set_trace()
        resp, body = manager.orchestration_client.create_stack(
            stack_name,
            region,
            template=template_data,
            parameters=parameters)
        print "response is %s" % resp
        print "body is %s" % body
        stack_id = resp['location'].split('/')[-1]
        stack_identifier = '%s/%s' % (stack_name, stack_id)
        cls.stacks.append({
            'client': manager.orchestration_client,
            'stack_id': stack_identifier
        })
        return stack_identifier

    @classmethod
    def get_stack(cls, manager, stack_id, region):
        """Returns the details of a single stack."""
        resp, body = manager.orchestration_client.get_stack(stack_id, region)
        if resp['status'] == '200':
            body = json.loads(body)
            return resp, body['stack']
        else:
            return resp, body

    @classmethod
    def get_api_version(cls, manager, region):
        resp, body = manager.orchestration_client.get_api_version(region)
        return resp, body


    @classmethod
    def delete_stack(cls, manager, stack_name, stack_id, region):
        resp, body = manager.orchestration_client.delete_stack(stack_name,
                                                               stack_id, region)
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

    @classmethod
    def list_stack(cls, manager):

        resp, body = manager.orchestration_client.list_stacks()
        return resp, body

    def update_stack(self, manager ,stack_identifier, name,
                     disable_rollback=True,
                     parameters={}, timeout_mins=60, template=None,
                     template_url=None):
        headers, body = self._prepare_update_create(
            name,
            disable_rollback,
            parameters,
            timeout_mins,
            template,
            template_url)

        uri = "stacks/%s" % stack_identifier
        resp, body = self.put(uri, headers=headers, body=body)
        return resp, body

    def _prepare_update_create(self, name, disable_rollback=True,
                               parameters={}, timeout_mins=60,
                               template=None, template_url=None):
        post_body = {
            "stack_name": name,
            "disable_rollback": disable_rollback,
            "parameters": parameters,
            "timeout_mins": timeout_mins
            #"template": "HeatTemplateFormatVersion: '2013-05-23'\n"
        }
        if template:
            post_body['template'] = template
        if template_url:
            post_body['template_url'] = template_url
        body = json.dumps(post_body, default=datehandler)

        # Password must be provided on stack create so that heat
        # can perform future operations on behalf of the user
        headers = dict(self.headers)
        headers['X-Auth-Key'] = self.password
        headers['X-Auth-User'] = self.user
        return headers, body

def datehandler(obj):
        if isinstance(obj, datetime.date):
               return str(obj)
        else:
               raise TypeError, 'Object of type %s with value of %s is not ' \
                         'JSON serializable' % (type(obj), repr(obj))