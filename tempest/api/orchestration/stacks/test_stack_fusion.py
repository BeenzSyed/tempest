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
import yaml


LOG = logging.getLogger(__name__)


class StacksTestJSON(base.BaseOrchestrationTest):
    _interface = 'json'

    @classmethod
    def setUpClass(cls):
        super(StacksTestJSON, cls).setUpClass()
        cls.client = cls.orchestration_client

    def test_fusion(self):
        regionsConfig = self.config.orchestration['regions']
        regions = regionsConfig.split(",")
        for region in regions:
            self.buildinfo(region)
            self.templates_in_fusion(region)
            self.get_template_catalog(region)
            self.get_rax_templates(region)
            self.get_all_templates(region)
            self.get_custom_templates(region)
            self.get_single_template(region)
            self.get_list_of_stacks(region)
            self.get_template_catalog_with_metadata(region)
            self.get_single_template_with_metadata(region)
            self.create_stack_with_supported_template_id(region)
            self.create_stack_with_supported_template(region)
            self.stack_show_call(region)
            self.stack_show_call_with_details(region)
            #self.stack_show_call_checkmate_migration(region)
            self.stack_update(region)
            self.stack_preview(region)

    def buildinfo(self, region):
        account = self.config.identity['username']
        print "\nTest using %s in region %s" % (account, region)
        respbi, bodybi = self.orchestration_client.get_build_info(region)
        print "The build info is: %s" % bodybi

    def get_template_catalog(self, region):
        print "\nTest get template catalog:"
        resp, body = self.orchestration_client.get_template_catalog(
            region=region)
        self.assertEqual(resp['status'], '200', "expected response was 200 "
                                            "but actual was %s. Body %s" % (resp['status'], body))

    def get_rax_templates(self, region):
        print "\nTest get rax templates:"
        resp, body = self.orchestration_client.get_rax_templates(region=region)
        self.assertEqual(resp['status'], '200', "expected response was 200 "
                                            "but actual was %s. Body %s" % (resp['status'], body))

    def get_all_templates(self, region):
        print "\nTest get all templates:"
        resp, body = self.orchestration_client.get_all_templates(region=region)
        self.assertEqual(resp['status'], '200', "expected response was 200 "
                                            "but actual was %s. Body %s" % (resp['status'], body))

    def get_custom_templates(self, region):
        print "\nTest get custom templates:"
        resp, body = self.orchestration_client.get_custom_templates(region=region)
        self.assertEqual(resp['status'], '200', "expected response was 200 "
                                            "but actual was %s. Body %s" % (resp['status'], body))

    def get_single_template(self, region):
        print "\nTest get a single template:"
        template_id = "wordpress-single"
        resp, body = self.orchestration_client.get_single_template(
            template_id=template_id, region=region)
        self.assertEqual(resp['status'], '200', "expected response was 200 "
                                            "but actual was %s. Body %s" % (resp['status'], body))

    def get_template_catalog_with_metadata(self, region):
        print "\nTest get template catalog with metadata:"
        resp, body = self.orchestration_client.\
            get_template_catalog_with_metadata(region=region)
        for template in body['templates']:
            if 'rackspace-metadata' in template:
                print"Templates %s have metadata" % template['id']
            else:
                print "Templates %s does not have metadata" % template['id']

    def get_single_template_with_metadata(self, region):
        print "\nTest get a single template with metadata:"
        template_id = "wordpress-single"
        resp, body = self.orchestration_client.\
            get_single_template_with_metadata(template_id=template_id,
                                              region=region)
        if body['template']['rackspace-metadata']:
            print "Template %s call responded with metadata" % template_id
        else:
            print "Test fail to get metadata of %s" % template_id

    def get_list_of_stacks(self, region):
        print "\nTest get a list of stacks:"
        resp, body = self.orchestration_client.get_list_of_stacks_fusion\
                (region=region)
        self.assertEqual(resp['status'], '200', "expected response was 200 "
                                            "but actual was %s. Body %s" % (resp['status'], body))

    def create_stack_with_supported_template_id(self, region, template=None):
        print "\nTest create stack with supported template id:"
        template_id = self.config.orchestration['template']

        if template_id == None:
            #Use default
            template_id = "wordpress-single"

        parameters = {}
        # parameters= {"ssh_keypair_name": "foo",
        #             "ssh_sync_keypair_name": "foo"}
        stack_name = rand_name("fusion_"+template_id+region)
        resp, body = self.orchestration_client.create_stack_fusion(
            name=stack_name, region=region, template_id=template_id,
            parameters=parameters)
        self.assertEqual(resp['status'], '201', "expected response was 201 "
                                            "but actual was %s. Body %s" % (resp['status'], body))
        stack_identifier = body['stack']['id']
        if resp['status'] == '201':
            stack_id = body['stack']['id']
            url = "stacks/%s/%s?with_support_info=1" % (stack_name, stack_id)
            resp, body = self.orchestration_client.get_stack_info_for_fusion(
                url=url, region=region)
            self.assertEqual(body['stack']['rackspace_template'], True,)
            self.assertIn('template_id', body['stack'])
        dresp, dbody = self.delete_stack(stackname=stack_name,
                                         stackid=stack_identifier,
                                         region=region)

    def create_stack_with_supported_template(self, region):
        print "\nTest create stack with supported template:"
        # Unsupported Template with flag as False
        resp, body = self.orchestration_client.get_template_catalog(
            region=region)
        for template in body['templates']:
            if template['id'] == "lamp":
                yaml_template = template
                yaml_template.pop("version", None)
                yaml_template.pop("id", None)
                yaml_template.pop("metadata", None)
                parameters={}
                break
        stack_name = rand_name("Fusion_")
        resp, body = self.orchestration_client.create_stack_fusion(
            name=stack_name, region=region, template_id=None,
            #template=template,
            template=yaml.safe_dump(yaml_template),
            parameters=parameters)
        self.assertIn(resp['status'], ['200', '201'])
        stack_identifier = body['stack']['id']
        if resp['status'] == '200':
            stack_id = body['stack']['id']
            url = "stacks/%s/%s?with_support_info=1" % (stack_name, stack_id)
            resp, body = self.orchestration_client.get_stack_info_for_fusion(
                url=url, region=region)
            self.assertEqual(body['stack']['rackspace_template'], False,)
            self.assertEqual(body['stack']['application_name'],\
                                          ('(Not Specified)'),
                             "Expected was not specified but has "
                             "application name")
            self.assertNotIn('template_id', body['stack'])
        dresp, dbody = self.delete_stack(stackname=stack_name,
                                         stackid=stack_identifier,
                                         region=region)

    def stack_show_call(self, region):
        print "\nTest get stack with support info:"
        template_id = "wordpress-single"
        parameters = {}
        stack_name = rand_name("fusion_"+template_id+region)
        resp, body = self.orchestration_client.create_stack_fusion(
            name=stack_name, region=region, template_id=template_id,
            parameters=parameters)

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

    def stack_show_call_with_details(self, region):
        print "\nTest get stack details with support info"
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

    # def stack_show_call_checkmate_migration(self, region):
    #     print "Test get stack details with support info"
    #     url = "stacks/detail?with_support_info=1"
    #     resp, body = self.orchestration_client.get_stack_info_for_fusion(
    #             url, region)
    #
    #     for stack in body['stacks']:
    #         if 'rackspace_template' in stack:
    #             if stack['rackspace_template']==False:
    #
    #                 self.assertEqual(stack['application_name'],('(Not Specified)'),
    #                                 "Expected was WordPress but has "
    #                                  " no application name")
    #                 self.assertNotIn('template_id', stack)
    #
    #             if stack['rackspace_template']==True:
    #                 self.assertIn('template_id', stack)
    #                 self.assertEqual(stack['application_name'],('WordPress'),
    #                                  "Expected was not specified but has "
    #                                  "application name")

    def stack_preview(self, region):
        print "\nTest get stack preview"
        template_id = "wordpress-single"
        parameters = {}
        # parameters= {"ssh_keypair_name": "foo",
        #             "ssh_sync_keypair_name": "foo"}
        stack_name = rand_name("fusion_"+template_id+region)
        resp_temp, body_temp = self.orchestration_client.get_single_template(
            template_id,region)
        resp, body = self.orchestration_client.stack_preview(
            stack_name, region, template_id, parameters=parameters)
        self.assertEqual(resp['status'], '200', "expected response was 200 "
                                            "but actual was %s. Body: %s "% (resp['status'], body))
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
        self.comp_list(response_resource_list, template_resource_list)

    def stack_update(self, region):
        print "\nTest update stack"
        template_id = "wordpress-single"
        parameters = {}
        # parameters= {"ssh_keypair_name": "OMG",
        #              "ssh_sync_keypair_name": "OMG"}
        stack_name =rand_name("fusion_test_"+template_id+region)
        resp, body = self.orchestration_client.create_stack_fusion(
            stack_name, region, template_id, parameters=parameters)
        self.assertEqual(resp['status'], '201', "expected response was 201 "
                                            "but actual was %s. Body %s" % (resp['status'], body))
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
                              "expected response was 202"
                        "but actual was %s. Body %s" % (resp['status'], body))
             dresp, dbody = self.delete_stack(stack_name, stack_identifier,
                                            region)

    def templates_in_fusion(self, region):
        print "\nTest template storage in swift"
        '''todo: Change assert in get_all_templates after fusion modification'''

        template = {"heat_template_version": "2013-05-23", "description": "Simple template to deploy a single compute instance", "resources": {"my_instance": {"type": "OS::Nova::Server", "properties": {"key_name": "primkey", "image": "CentOS 6.5", "flavor": "m1.small"}}}}
        new_template = {"heat_template_version": "2013-05-23", "description": "Simple template to deploy a single compute instance with an updated description to test", "resources": {"my_instance": {"type": "OS::Nova::Server", "properties": {"key_name": "primkey", "image": "CentOS 6.5", "flavor": "m1.small"}}}}

        resp, body = self.orchestration_client.get_template_catalog(region)
        print "\nGot template catalog from fusion\n\nStoring a template in fusion to test storage"

        parameters = {}
        stack_name = rand_name("fusion_"+region)
        resp, body = self.orchestration_client.store_stack_fusion(
            stack_name, region, template=template, parameters=parameters)
        self.assertIn(resp['status'], ['200', '201'])
        template_id = body['template_id']
        print "Template stored. ID = " + str(template_id) + "\n\nGetting the template we just stored...ID = " + str(template_id)

        # #check swift
        # ipdb.set_trace()
        # resp, body = self.swift_client.list_auth_swift_object(
        #     storage_id=template_id,
        #     region=region)
        # if resp['status'] == ('200'):
        #     print "Swift has the template."

        #verify existence and contents:
        gresp, gbody = self.orchestration_client.get_template(template_id, region)
        self.assertEqual('200', gresp['status'], "Response to get should be 200")
        self.assertEqual(template, gbody['template'], "Template we sent should equal the one we get back")
        #self.comp_stored_template(template, gbody)
        print "Got template and it was the same" + "\n\nUpdating the same template to test updating..ID = " + str(template_id)

        #testing PUT on an existing template (the one we added with POST) and check status code
        uresp, ubody = self.orchestration_client.update_template(template_id, new_template, region, stack_name)
        self.assertEqual('200', uresp['status'], "Body %s" % ubody)
        gresp, gbody = self.orchestration_client.get_template(template_id, region)
        self.assertEqual('200', gresp['status'], "Body %s" % gbody)
        print "The update request was successful, and the template still exists after update."
        self.assertEqual(new_template, gbody['template'], "Template we sent should equal the one we get back")
        #self.comp_stored_template(new_template, gbody)

        #fetch all templates
        aresp, abody = self.orchestration_client.get_custom_templates(region)
        for template in abody['templates']:
            if template_id == template['id']:
                self.assertEqual(new_template['description'], template['description'], "Updated template verified")
                self.assertEqual(new_template, template['template'], "Templates match")

        #deleting the template we added to fusion earlier and check status code
        print "The changes to the template have happened correctly." "\n\nDeleting the template we have stored...ID = " + str(template_id)
        dresp, dbody = self.orchestration_client.delete_template(template_id, region)
        self.assertEqual('200', dresp['status'], "Body %s" % dbody)
        print "Template deleted?" + "\n\nMaking sure a GET on the deleted template fails...ID = " + str(template_id)

        #verify non-existence
        gresp, gbody = self.orchestration_client.get_template(template_id, region)
        self.assertEqual('404', gresp['status'], "Body %s" % gbody)
        print "GET failed like it should."

    def comp_stored_template(self, template_sent, template_from_get):
        actual_template = template_from_get['template']
        del actual_template['id']
        del actual_template['metadata']
        self.assertEqual(template_sent, actual_template, "Template we sent should equal the one we get back")
        template_sent['eric'] = 'Eric'
        self.assertNotEqual(template_sent, actual_template, "Make sure things don't have false positives")

        #self.assertIn('template_id', body['stack'])
        #dresp, dbody = self.delete_stack(stack_name, stack_identifier, region)

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
        else:
            print"Resources in template and stack_preview response are same"
