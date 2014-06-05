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

from tempest.scenario import manager
from tempest.test import services
from tempest.common.utils.data_utils import rand_name


class FusionClientTest(manager.FusionScenarioTest):

    def setUp(self):
        super(FusionClientTest, self).setUp()
        self.client = self.fusion_client


    def launch_stack(self):

        template_id="wordpress-single",
        stack_name=rand_name("fusion_client_")
        parameters={}

        body = self.client.stacks.create(
            template_id="wordpress-single",
            stack_name=stack_name,
            parameters=parameters)
        stack_id = body['stack']['id']
        self.stack = self.client.stacks.get(stack_id)
       # self.stack_identifier = '%s/%s' % (self.stack_name, self.stack.id)



    def test_launch_stack_by_template_id(self):

        self.launch_stack()
