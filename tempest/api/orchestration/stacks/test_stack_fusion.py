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
import time

from tempest.api.orchestration import base
from tempest.common.utils.data_utils import rand_name
from tempest.openstack.common import log as logging
from testconfig import config
import yaml

LOG = logging.getLogger(__name__)


class StacksTestJSON(base.BaseOrchestrationTest):
    _interface = 'json'

    @classmethod
    def setUpClass(cls):
        super(StacksTestJSON, cls).setUpClass()
        cls.client = cls.orchestration_client

    def test_get_template_catalog(self):
        region = "DFW"
        resp, body = self.orchestration_client.get_template_catalog(region)
        self.assertEqual(resp['status'], '200', "expected response was 200 "
                                            "but actual was %s"%resp['status'])

    def test_get_single_template(self):
        region = "DFW"
        template_id = "wordpress-single"
        resp, body = self.orchestration_client.get_single_template(
            template_id, region)
        self.assertEqual(resp['status'], '200', "expected response was 200 "
                                            "but actual was %s"%resp['status'])

    def test_get_template_catalog_with_metadata(self):
        region = "DFW"
        resp, body = self.orchestration_client.get_template_catalog_with_metadata(region)
        #print resp, body
        for template in body['templates']:
            if 'rackspace-metadata' in template:
                print"Templates  %s have metadata"%template['id']
            else:
                print "Templates  %s does not have metadata"%template['id']

    def test_get_single_template_with_metadata(self):
        region = "DFW"
        template_id = "wordpress-single"
        resp, body = self.orchestration_client.get_single_template_with_metadata(
            template_id, region)
        if body['template']['rackspace-metadata']:
            print "Template %s call responded with metadata" %template_id
        else:
            print "Test fail to get metadata of %s" %template_id

    def test_get_list_of_stacks(self):
        region = "DFW"
        resp, body = self.orchestration_client.get_list_of_stacks_fusion(region)
        self.assertEqual(resp['status'], '200', "expected response was 200 "
                                            "but actual was %s"%resp['status'])

    def test_create_stack_with_supported_template_id(self, template=None):
        template_id = self.config.orchestration['template']

        if template_id == None:
            #Use default
            template_id = "wordpress-single"

        region = "DFW"
        parameters = {}
        # parameters= {"ssh_keypair_name": "foo",
        #             "ssh_sync_keypair_name": "foo"}
        stack_name = rand_name("fusion_"+template_id+region)
        resp, body = self.orchestration_client.create_stack_fusion(
            stack_name, region, template_id, parameters=parameters)
        self.assertEqual(resp['status'], '201', "expected response was 201 "
                                            "but actual was %s"%resp['status'])
        stack_identifier = body['stack']['id']
        if resp['status'] == '201':
            stack_id = body['stack']['id']
            url = "stacks/%s/%s?with_support_info=1" % (stack_name, stack_id)
            resp, body = self.orchestration_client.get_stack_info_for_fusion(
                url, region)
            print "For test "         
            print "printing body %s " % body
            print "only for test"
            self.assertEqual(body['stack']['rackspace_template'], True,)
            # self.assertEqual(body['stack']['application_name'],\
            #                               ('WordPress'),
            #                  "Expected wasWordpress but has "
            #                  "no application name")
            self.assertIn('template_id', body['stack'])
        dresp, dbody = self.delete_stack(stack_name, stack_identifier, region)

    def test_create_stack_with_supported_template(self):
        # Unsupported Template with flag as False
        region = "DFW"
        resp, body = self.orchestration_client.get_template_catalog(region)
        for template in body['templates']:
             if template['id'] == "wordpress-single":
                 yaml_template = template
                 yaml_template.pop("version", None)
                 yaml_template.pop("id", None)
                 yaml_template.pop("metadata", None)
                 parameters={}
                 # parameters= {"ssh_keypair_name": "foo",
                 #          "ssh_sync_keypair_name": "foo"}
                 break

        region = "DFW"
        stack_name = rand_name("Fusion_")
        resp, body = self.orchestration_client.create_stack_fusion(stack_name,
                                                                   region,
                                              template_id = None,
                                              template = yaml.safe_dump(
                                                  yaml_template),
                                              parameters=parameters)
        self.assertEqual(resp['status'], '201', "expected response was 201 "
                                            "but actual was %s"%resp['status'])
        stack_identifier = body['stack']['id']
        if resp['status']== '201':
            stack_id = body['stack']['id']
            url = "stacks/%s/%s?with_support_info=1"%(stack_name,stack_id)
            resp, body = self.orchestration_client.get_stack_info_for_fusion(
                url, region)
            self.assertEqual(body['stack']['rackspace_template'], False,)
            self.assertEqual(body['stack']['application_name'],\
                                          ('(Not Specified)'),
                             "Expected was not specified but has "
                             "application name")
            self.assertNotIn('template_id', body['stack'])
        dresp, dbody = self.delete_stack(stack_name, stack_identifier, region)

    def test_stack_show_call(self):
        region = "DFW"
        url = "stacks?with_support_info"
        resp, body = self.orchestration_client.get_stack_info_for_fusion(
                url, region)
        for stack in body['stacks']:
            if 'rackspace_template' in stack:
                if stack['rackspace_template']==False:

                    self.assertEqual(stack['application_name'],('(Not Specified)'),
                                     "Expected was not specified but has "
                                     "application name")
                    self.assertNotIn('template_id', stack)

                if stack['rackspace_template']==True:
                    self.assertIn('template_id', stack)
                    self.assertEqual(stack['application_name'],('WordPress'),
                                     "Expected was WordPress but has "
                                     " no application name")

    def test_stack_show_call_with_details(self):
        region = "DFW"
        url = "stacks/detail?with_support_info"
        resp, body = self.orchestration_client.get_stack_info_for_fusion(
                url, region)

        for stack in body['stacks']:
            if 'rackspace_template' in stack:
                if stack['rackspace_template']==False:

                    self.assertEqual(stack['application_name'],('(Not Specified)'),
                                    "Expected was WordPress but has "
                                     " no application name")
                    self.assertNotIn('template_id', stack)

                if stack['rackspace_template']==True:
                    self.assertIn('template_id', stack)
                    self.assertEqual(stack['application_name'],('WordPress'),
                                     "Expected was not specified but has "
                                     "application name")

    def test_stack_show_call_checkmate_migration(self):
        region = "IAD"
        url = "stacks/detail?with_support_info=1"
        resp, body = self.orchestration_client.get_stack_info_for_fusion(
                url, region)

        print resp
        print body

        for stack in body['stacks']:
            if 'rackspace_template' in stack:
                if stack['rackspace_template']==False:

                    self.assertEqual(stack['application_name'],('(Not Specified)'),
                                    "Expected was WordPress but has "
                                     " no application name")
                    self.assertNotIn('template_id', stack)

                if stack['rackspace_template']==True:
                    self.assertIn('template_id', stack)
                    self.assertEqual(stack['application_name'],('WordPress'),
                                     "Expected was not specified but has "
                                     "application name")

    def test_stack_preview(self):
        template_id = "wordpress-single"
        region = "DFW"
        parameters = {}
        # parameters= {"ssh_keypair_name": "foo",
        #             "ssh_sync_keypair_name": "foo"}
        stack_name = rand_name("fusion_"+template_id+region)
        resp_temp, body_temp = self.orchestration_client.get_single_template(
            template_id,region)
        resp, body = self.orchestration_client.stack_preview(
            stack_name, region, template_id, parameters=parameters)
        self.assertEqual(resp['status'], '200', "expected response was 200 "
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
        parameters={}
        # parameters= {"ssh_keypair_name": "OMG",
        #              "ssh_sync_keypair_name": "OMG"}
        stack_name =rand_name("fusion_test_"+template_id+region)
        resp,body = self.orchestration_client.create_stack_fusion(
            stack_name, region, template_id, parameters=parameters)
        self.assertEqual(resp['status'], '201', "expected response was 201 "
                                            "but actual was %s"%resp['status'])

        stack_identifier = body['stack']['id']
        stack_id = "%s/%s" % (stack_name, stack_identifier)
        resp, body = self.get_stack(stack_id, region)
        count = 0
        while body['stack_status'] == 'CREATE_IN_PROGRESS' and count < 20:
            resp, body = self.get_stack(stack_id, region)
            if resp['status'] == '200':
                print "Deployment in %s status. Checking again in 1 minute" % \
                   body['stack_status']
                time.sleep(60)
                count += 1
                if body['stack_status'] == 'CREATE_FAILED':
                            print "Stack create failed. Here's why: %s" % body['stack_status_reason']
                if count == 20:
                   print "Stack create has taken over 20 minutes. Force " \
                        "failing now."
                   self._delete_stack(stack_name, stack_id, region)
            elif resp['status'] != '200':
                print "The response is: %s" % resp
            else:
                print "Something went wrong. Here's what: %s, %s" % (resp, body)
        if body['stack_status'] == 'CREATE_COMPLETE':
             resp_update, body_update = self.orchestration_client\
                       .update_stack_fusion(stack_identifier,stack_name,region,
                                   template_id=template_id,template={},parameters=parameters)
             self.assertEqual(resp_update['status'], '202',
                              "expected response was"
                        " 202 but actual was %s"%resp_update['status'])
             dresp, dbody = self.delete_stack(stack_name, stack_identifier,
                                            region)

    def test_store_template_in_fusion(self, template=None):
        template_id = self.config.orchestration['template']

        if template == None:
            #Use default
            template = """
            {"heat_template_version": "2013-05-23", "description": "Simple template to deploy a single compute instance", "resources": {"my_instance": {"type": "OS::Nova::Server", "properties": {"key_name": "primkey", "image": "CentOS 6.5", "flavor": "m1.small"}}}}}
            """

        region = "DFW"
        parameters = {}
        # parameters= {"ssh_keypair_name": "foo",
        #             "ssh_sync_keypair_name": "foo"}
        stack_name = rand_name("fusion_"+region)
        resp, body = self.orchestration_client.store_stack_fusion(
            stack_name, region, template, parameters=parameters)
        self.assertEqual(resp['status'], '201', "expected response was 201 "
                                            "but actual was %s"%resp['status'])
        stack_identifier = body['stack']['id']
        if resp['status'] == '201':
            stack_id = body['stack']['id']
            url = "stacks/%s/%s?with_support_info=1" % (stack_name, stack_id)
            resp, body = self.orchestration_client.get_stack_info_for_fusion(
                url, region)
            print "For test "
            print "printing body %s " % body
            print "only for test"
            self.assertEqual(body['stack']['rackspace_template'], True,)
            # self.assertEqual(body['stack']['application_name'],\
            #                               ('WordPress'),
            #                  "Expected wasWordpress but has "
            #                  "no application name")
            self.assertIn('template_id', body['stack'])
        dresp, dbody = self.delete_stack(stack_name, stack_identifier, region)

    def test_templates_in_fusion(self):
        region = "DFW"

        template = """
            {"heat_template_version": "2013-05-23", "description": "Simple template to deploy a single compute instance", "resources": {"my_instance": {"type": "OS::Nova::Server", "properties": {"key_name": "primkey", "image": "CentOS 6.5", "flavor": "m1.small"}}}}}
            """
        self.test_store_template_in_fusion(template)

        template_id = 1 #...
        #verify response
        #exists
        #compare
        new_template = """
            {"heat_template_version": "2013-05-23", "description": "Simple template to deploy a single compute instance with an updated description to test", "resources": {"my_instance": {"type": "OS::Nova::Server", "properties": {"key_name": "primkey", "image": "CentOS 6.5", "flavor": "m1.small"}}}}}
            """
        uresp, ubody = self.orchestration_client.update_template(template_id, new_template, region)
        print uresp

        self.assertEqual('202', uresp['status'], "Response to update should be 202 accept")

        #verify response
        #exists
        #compare



        dresp, dbody = self.orchestration_client.delete_template(template_id, region)
        print dresp

        self.assertEqual('204', dresp['status'], "Response to delete should be 204 no content")

        #verify response -> non-existing

    def test_update_template_in_fusion(self, template=None):
        #store a template
        template_id = self.config.orchestration['template']

        if template == None:
            #Use default
            template = """
            {"heat_template_version": "2013-05-23", "description": "Simple template to deploy a single compute instance", "resources": {"my_instance": {"type": "OS::Nova::Server", "properties": {"key_name": "primkey", "image": "CentOS 6.5", "flavor": "m1.small"}}}}}
            """

        region = "DFW"
        parameters = {}
        # parameters= {"ssh_keypair_name": "foo",
        #             "ssh_sync_keypair_name": "foo"}
        stack_name = rand_name("fusion_"+region)

        #does this store a template?
        #or does store_stack mean something else
        resp, body = self.orchestration_client.store_stack_fusion(
            stack_name, region, template, parameters=parameters)
        self.assertEqual(resp['status'], '201', "expected response was 201 "
                                            "but actual was %s"%resp['status'])
        #now update the template and verify

        #change something
        template = """
            {"heat_template_version": "2013-05-23", "description": "Simple template to deploy a single compute instance with an updated description to test", "resources": {"my_instance": {"type": "OS::Nova::Server", "properties": {"key_name": "primkey", "image": "CentOS 6.5", "flavor": "m1.small"}}}}}
            """
        #description is slightly different
        resp, body = self.orchestration_client.update_stack_fusion(stack_name, region, template, parameters=parameters)

        #verify changes
        self.assertEqual(resp['status'], '201', "expected response was 201 "
                                            "but actual was %s"%resp['status'])
        stack_identifier = body['stack']['id']
        if resp['status'] == '201':
            stack_id = body['stack']['id']
            url = "stacks/%s/%s?with_support_info=1" % (stack_name, stack_id)
            resp, body = self.orchestration_client.get_stack_info_for_fusion(
                url, region)
            print "For test "
            print "printing body %s " % body
            print "only for test"
            self.assertEqual(body['stack']['rackspace_template'], True,)
            # self.assertEqual(body['stack']['application_name'],\
            #                               ('WordPress'),
            #                  "Expected wasWordpress but has "
            #                  "no application name")
            self.assertIn('template_id', body['stack'])
        dresp, dbody = self.delete_stack(stack_name, stack_identifier, region)


    def test_delete_template_in_fusion(self, template=None):
        template_id = self.config.orchestration['template']

        if template == None:
            #Use default
            template = """
            {"heat_template_version": "2013-05-23", "description": "Simple template to deploy a single compute instance", "resources": {"my_instance": {"type": "OS::Nova::Server", "properties": {"key_name": "primkey", "image": "CentOS 6.5", "flavor": "m1.small"}}}}}
            """

        region = "DFW"
        parameters = {}
        # parameters= {"ssh_keypair_name": "foo",
        #             "ssh_sync_keypair_name": "foo"}
        stack_name = rand_name("fusion_"+region)
        resp, body = self.orchestration_client.store_stack_fusion(
            stack_name, region, template, parameters=parameters)
        self.assertEqual(resp['status'], '201', "expected response was 201 "
                                            "but actual was %s"%resp['status'])
        stack_identifier = body['stack']['id']

        #it exists, now delete
        #does this delete a template?
        #doesn't seem like it does
        dresp, dbody = self.delete_stack(stack_name, stack_identifier, region)

        #now make sure it is gone

        stack_identifier = body['stack']['id']
        if resp['status'] == '201':
            stack_id = body['stack']['id']
            url = "stacks/%s/%s?with_support_info=1" % (stack_name, stack_id)
            resp, body = self.orchestration_client.get_stack_info_for_fusion(
                url, region)

            if resp['status'] == '201' or resp['status'] == '200':
                self.fail("template was removed and should not exist.")



    def comp_list(self, list1, list2):
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
