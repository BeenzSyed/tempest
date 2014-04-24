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
        template_id="wordpress-single"
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
                print"Templates  %s have metadata"%template['id']
            else :
                print "Templates  %s does not have metadata"%template['id']


    def test_get_single_template_with_metadata(self):
        region = "IAD"
        template_id="wordpress-single"
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

        template_id = "wordpress-single"
        region = "IAD"
        parameters= {"ssh_keypair_name": "foo",
                    "ssh_sync_keypair_name": "foo"}
        stack_name = rand_name("fusion_"+template_id+region)
        resp,body = self.orchestration_client.create_stack_fusion(
            stack_name, region, template_id, parameters=parameters)
        self.assertEqual(resp['status'], '201', "expected response was 201 "
                                            "but actual was %s"%resp['status'])
        stack_identifier = body['stack']['id']
        if resp['status']== '201':
            stack_id = body['stack']['id']
            url = "stacks/%s/%s?with_support_info"%(stack_name,stack_id)
            resp,body = self.orchestration_client.get_stack_info_for_fusion(
                url,region)
            self.assertEqual(body['stack']['rackspace_template'],True,)
            self.assertEqual(body['stack']['application_name'],\
                                          ('(Not Specified)'),
                             "Expected was not specified but has "
                             "application name")
            self.assertIn('template_id', body['stack'])
        dresp, dbody = self.delete_stack(stack_name, stack_identifier,region)


    def test_create_stack_with_supported_template(self):
        # Unsupported Template with flag as False
        region = "IAD"
        resp , body = self.orchestration_client.get_template_catalog(region)
        for template in body['templates']:
             if template['id'] == "wordpress-single":
                 yaml_template = template
                 yaml_template.pop("version", None)
                 yaml_template.pop("id", None)
                 yaml_template.pop("metadata", None)
                 parameters= {"ssh_keypair_name": "foo",
                          "ssh_sync_keypair_name": "foo"}
                 break

        region = "IAD"
        stack_name = rand_name("Fusion_")
        resp, body = self.orchestration_client.create_stack_fusion(stack_name,
                                                                   region,
                                              template_id=None,
                                              template=yaml.safe_dump(
                                                  yaml_template),
                                              parameters=parameters)
        self.assertEqual(resp['status'], '201', "expected response was 201 "
                                            "but actual was %s"%resp['status'])
        stack_identifier = body['stack']['id']
        if resp['status']== '201':
            stack_id = body['stack']['id']
            url = "stacks/%s/%s?with_support_info"%(stack_name,stack_id)
            resp,body = self.orchestration_client.get_stack_info_for_fusion(
                url,region)
            self.assertEqual(body['stack']['rackspace_template'],False,)
            self.assertEqual(body['stack']['application_name'],\
                                          ('(Not Specified)'),
                             "Expected was not specified but has "
                             "application name")
            self.assertNotIn('template_id', body['stack'])
        dresp, dbody = self.delete_stack(stack_name, stack_identifier,region)

    def test_stack_show_call(self):
        region = "IAD"
        url = "stacks?with_support_info"
        resp,body = self.orchestration_client.get_stack_info_for_fusion(
                url,region)
        for stack in body['stacks']:
            if 'rackspace_template' in stack:
                if stack['rackspace_template']==False:

                    self.assertEqual(stack['application_name'],('(Not Specified)'),
                                     "Expected was not specified but has "
                                     "application name")
                    self.assertNotIn('template_id', stack)

                if stack['rackspace_template']==True:
                    self.assertIn('template_id', stack)
                    self.assertEqual(stack['application_name'],('(Not Specified)'),
                                     "Expected was not specified but has "
                                     "application name")

    def test_stack_show_call_with_details(self):
        region = "IAD"
        url = "stacks/detail?with_support_info"
        resp,body = self.orchestration_client.get_stack_info_for_fusion(
                url,region)

        for stack in body['stacks']:
            if 'rackspace_template' in stack:
                if stack['rackspace_template']==False:

                    self.assertEqual(stack['application_name'],('(Not Specified)'),
                                     "Expected was not specified but has "
                                     "application name")
                    self.assertNotIn('template_id', stack)

                if stack['rackspace_template']==True:
                    self.assertIn('template_id', stack)
                    self.assertEqual(stack['application_name'],('(Not Specified)'),
                                     "Expected was not specified but has "
                                     "application name")

    def test_stack_preview(self):
        template_id = "wordpress-single"
        region = "IAD"
        parameters= {"ssh_keypair_name": "foo",
                    "ssh_sync_keypair_name": "foo"}
        stack_name = rand_name("fusion_"+template_id+region)
        resp_temp , body_temp = self.orchestration_client.get_single_template(
            template_id,region)
        resp,body = self.orchestration_client.stack_preview(
            stack_name, region, template_id, parameters=parameters)
        self.assertEqual(resp['status'], '200', "expected response was 201 "
                                            "but actual was %s"%resp['status'])
        response_resource_list = []
        for resource in body['stack']['resources']:
            response_resource_list.append(resource['resource_type'])
        response_resource_list.sort()
        template_resource_list = []
        resources_temp = body_temp['template']['resources']
        for key, value in resources_temp.iteritems():
            resource = value['type']
            template_resource_list.append(resource)
        template_resource_list.sort()
        self.comp_list(response_resource_list,template_resource_list)

    def test_stack_update(self):

        template_id = "wordpress-single"
        region = "QA"
        parameters= {"ssh_keypair_name": "OMG",
                     "ssh_sync_keypair_name": "OMG"}
        stack_name =rand_name("fusion_test_"+template_id+region)
        resp,body = self.orchestration_client.create_stack_fusion(
            stack_name, region, template_id, parameters=parameters)
        self.assertEqual(resp['status'], '201', "expected response was 201 "
                                            "but actual was %s"%resp['status'])

        stack_identifier = body['stack']['id']
        stack_id = "%s/%s" % (stack_name,stack_identifier)
        resp_get_stack, body_get_stack = self.get_stack(stack_id, region)
        if body_get_stack['stack']['stack_status'] =="CREATE_FAILED":
            print "stack creation failed for reason : %s"%(body_get_stack['stack']['stack_status_reason'])
        elif body_get_stack['stack']['stack_status'] in("CREATE_IN_PROGRESS","CREATE_COMPLETE"):

            resp_update, body_update = self.orchestration_client\
             .update_stack_fusion(stack_identifier,stack_name,region,template_id=template_id,template={},parameters=parameters)
            self.assertEqual(resp_update['status'], '202', "expected response "
                                                         "was"
                                                       " 202 but actual was %s"%resp_update['status'])
        dresp, dbody = self.delete_stack(stack_name, stack_identifier,region)

    def comp_list(self ,list1, list2):
        Result = []
        for val in list1:
            if val in list2:
                Result.append(True)
            else :
               Result.append(False)
        if False in Result:
            print "Resources in template and stack_preview response are " \
                  "differnt"
        else :
            print"Resources in template and stack_preview response are same"