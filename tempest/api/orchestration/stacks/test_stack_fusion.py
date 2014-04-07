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




LOG = logging.getLogger(__name__)


class StacksTestJSON(base.BaseOrchestrationTest):
    _interface = 'json'

    @classmethod
    def setUpClass(cls):
        super(StacksTestJSON, cls).setUpClass()
        cls.client = cls.orchestration_client

    def test_get_template_catalog(self):
        region = "IAD"
        resp , body = self.orchestration_client.get_template_catalog(region)
        if self.assertEqual(resp['status'], '200'):
            print "Test get template catalog pass"
        else :
            print "Test get template catalog fail"


    def test_get_single_template(self):
        region = "IAD"
        template_id="wordpress-single-winserver"
        resp , body = self.orchestration_client.get_single_template(
            template_id,region)

        if self.assertEqual(resp['status'], '200'):
            print "Test get single template  pass"
        else :
            print "Test get single template fail"


    def test_get_template_catalog_with_metadata(self):
        region = "IAD"
        resp , body = self.orchestration_client.get_template_catalog_with_metadata(region)
       # print resp, body
        for template in body['templates']:
            if template['metadata']=={}:
                print""
            else :
                print "Templates does not have metadata"


    def test_get_single_template__with_metadata(self):
        region = "IAD"
        template_id="wordpress-single-winserver"
        resp , body = self.orchestration_client.get_single_template_with_metadata(
            template_id,region)
        if body['template']['metadata']:
            print"Template %s call responded with metadata" %template_id
        else:
           print"Test fail to get metadata of %s" %template_id

    def test_get_list_of_stacks(self):
        region = "IAD"
        resp , body = self.orchestration_client.get_list_of_stacks_fusion(region)
        if self.assertEqual(resp['status'], '200'):
            print "SUCCESS for get list call for Fusion"
        else :
            print "Test fail to get list call from fusion"


    def test_create_stack_with_supported_template_id(self):
        template_id = "wp-resource"
        region = "IAD"
        parameters={"key_name":'sabeen'}
        stack_name = rand_name("fusion_"+template_id+region)
        resp,body = self.orchestration_client.create_stack_fusion(
            stack_name,region,template_id,parameters=parameters)
        if self.assertEqual(resp['status'], '200'):
            print "Test create stack with supported template id : PASS "
        else:
            print "Test create stack with supported template id : FAIL "


    def test_create_stack_with_supported_template(self):

        region = "IAD"
        resp , body = self.orchestration_client.get_template_catalog(region)
        for template in body['templates']:
             if template['id'] == "wp-resource":
                 yaml_template = template
                 parameters={"key_name":'sabeen'}
                 break

        region = "IAD"
        stack_name = rand_name("qe_")
        resp,body =self.orchestration_client.create_stack_fusion(stack_name, region,
                                              template_id=None,
                                                template=yaml_template,
                                                parameters=parameters)


        if self.assertEqual(resp['status'], '200'):
            print "Test create stack with supported template: PASS "
        else:
            print "Test create stack with supported template: FAIL "

