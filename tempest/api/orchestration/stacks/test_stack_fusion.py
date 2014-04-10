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
import yaml



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
        self.assertEqual(resp['status'], '200', "expected response was 200 "
                                            "but actual was %s"%resp['status'])


    def test_get_single_template(self):
        region = "IAD"
        template_id="wordpress-single-winserver"
        resp , body = self.orchestration_client.get_single_template(
            template_id,region)
        self.assertEqual(resp['status'], '200', "expected response was 200 "
                                            "but actual was %s"%resp['status'])

    def test_get_template_catalog_with_metadata(self):
        region = "IAD"
        resp , body = self.orchestration_client.get_template_catalog_with_metadata(region)
        #print resp, body
        for template in body['templates']:
            if 'metadata' in template:
            #if template['metadata']=={}:
                print"Templates  %s have metadata"%template['id']
            else :
                print "Templates  %s does not have metadata"%template['id']


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
        self.assertEqual(resp['status'], '200', "expected response was 200 "
                                            "but actual was %s"%resp['status'])


    def test_create_stack_with_supported_template_id(self):

        template_id = "wordpress-single-winserver"
        region = "IAD"
        #{"key_name":'sabeen'}
        parameters = {}
        stack_name = rand_name("fusion_"+template_id+region)
        resp,body = self.orchestration_client.create_stack_fusion(
            stack_name, region, template_id, parameters=parameters)
        self.assertEqual(resp['status'], '201', "expected response was 201 "
                                            "but actual was %s"%resp['status'])


    def test_create_stack_with_supported_template(self):

        region = "IAD"
        resp , body = self.orchestration_client.get_template_catalog(region)
        for template in body['templates']:
             if template['id'] == "wordpress-single-winserver":
                 yaml_template = template
                 yaml_template.pop("version", None)
                 yaml_template.pop("id", None)
                 yaml_template.pop("metadata", None)
                 parameters ={}
                 break

        region = "IAD"
        stack_name = rand_name("fusion_")
        resp, body = self.orchestration_client.create_stack_fusion(stack_name,
                                                                   region,
                                              template_id=None,
                                              template=yaml.safe_dump(
                                                  yaml_template),
                                              parameters=parameters)
        self.assertEqual(resp['status'], '201', "expected response was 201 "
                                            "but actual was %s"%resp['status'])

        

