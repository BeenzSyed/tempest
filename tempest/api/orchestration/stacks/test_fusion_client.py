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
import time


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

    def test_get_single_template(self):
        template_id="wordpress-single"
        resp = self.client.templates.get(template_id)
        resp = resp.to_dict()
        self.assertIn('description',resp,)

    def test_single_template_with_metadata(self):
        template_id="wordpress-single"
        resp = self.client.templates.get(template_id,with_metadata=True)
        resp = resp.to_dict()
        self.assertIn('rackspace-metadata',resp,)

    def test_get_template_catalog(self):
        resp = self.client.templates.get_all()
        for template in resp:
            template = template.to_dict()
            self.assertIn('description', template)

    def test_get_template_catalog_with_metadata(self):
        resp = self.client.templates.get_all(with_metadata=True)
        for template in resp:
            template = template.to_dict()
            self.assertIn('rackspace-metadata', template)

    def test_get_list_of_stack(self):
        stacks = self.client.stacks.list()
        for stack in stacks:
            stack = stack.__dict__
            self.assertIn('stack_status', stack)

    def test_stack_preview(self):
        template_id = "wordpress-single"
        region = "DFW"
        parameters={}

        stack_name = rand_name("fusion_"+template_id+region)
        resp = self.client.templates.get(template_id,with_metadata=True)
        resp = resp.to_dict()
        body = self.client.stacks.preview(
            template_id="wordpress-single",
            stack_name=stack_name,
            parameters=parameters)
        body= body.to_dict()
        print "test"

        response_resource_list = []
        for resource in body['resources']:
            response_resource_list.append(resource['resource_type'])
        response_resource_list.sort()

        template_resource_list = []
        resources_temp = resp['resources']
        for key, value in resources_temp.iteritems():
            resource = value['type']
            template_resource_list.append(resource)
        template_resource_list.sort()

        self.comp_list(response_resource_list,template_resource_list)


# Need to fix this test
    def test_create_stack_with_supported_template_id(self):
        template_id = "wordpress-single"
        region = "QA"
        parameters={}
        stack_name = rand_name("fusion_"+template_id+region)
        body = self.client.stacks.create(
            template_id="wordpress-single",
            stack_name=stack_name,
            parameters=parameters)
        stack_id = body['stack']['id']
        body = self.client.stacks.get(stack_id,with_support_info=True)
        print "test"
        #self.assertIn('rackspace_template', body)
        #     self.assertEqual(body['stack']['rackspace_template'],True,)
        #     self.assertEqual(body['stack']['application_name'],\
        #                                   ('WordPress'),
        #                      "Expected wasWordpress but has "
        #                      "no application name")
        #     self.assertIn('template_id', body['stack'])
        # dresp, dbody = self.delete_stack(stack_name, stack_identifier,region)

    # Need to fix this test
    def test_get_supported_template(self):
         # Unsupported Template with flag as False
        region = "DFW"
        parameters={}
        template_id="wordpress-single"
        resp = self.client.templates.get(template_id,with_metadata=True)
        resp = resp.to_dict()
        stack_name = rand_name("Fusion_")
        body = self.client.stacks.create(
            template=resp,
            stack_name=stack_name,
            parameters=parameters)
        stack_id = body['stack']['id']
        print "test"

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
       # dresp, dbody = self.delete_stack(stack_name, stack_identifier,region)

    def test_stack_update(self):

        template_id = "wordpress-single"
        region = "DFW"
        parameters={}
        stack_name =rand_name("fusion_shwe_"+template_id+region)
        body = self.client.stacks.create(
            template_id="wordpress-single",
            stack_name=stack_name,
            parameters=parameters)
        stack_identifier = body['stack']['id']
        stack_id = "%s/%s" % (stack_name,stack_identifier)
        body = self.client.stacks.get(stack_id)
        count = 0
        body = body.to_dict()
        while body['stack_status'] == 'CREATE_IN_PROGRESS' and count < 20:
           body = self.client.stacks.get(stack_id)
           body = body.to_dict()

           print "Deployment in %s status. Checking again in 1 minute" % \
                   body['stack_status']
           time.sleep(60)
           count += 1
           if body['stack_status'] == 'CREATE_FAILED':
                            print "Stack create failed. Here's why: %s" % body['stack_status_reason']
           if count == 20:
                   print "Stack create has taken over 20 minutes. Force " \
                        "failing now."
                   self.client.stacks.delete(stack_id)
        if body['stack_status'] == 'CREATE_COMPLETE':
              body_update = self.client.stacks.update(stack_identifier,
                                   template_id=template_id,parameters=parameters)
              print "Done"

             #dresp, dbody = self.delete_stack(stack_name, stack_identifier,
              #                              region)



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
        else:
            print"Resources in template and stack_preview response are " \
                       "same"