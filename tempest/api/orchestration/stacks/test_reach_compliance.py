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

LOG = logging.getLogger(__name__)


class StacksTestJSON(base.BaseOrchestrationTest):
    _interface = 'json'

    @classmethod
    def setUpClass(cls):
        super(StacksTestJSON, cls).setUpClass()
        cls.client = cls.orchestration_client

    def test_compliance(self):
        regionsConfig = self.config.orchestration['regions']
        regions = regionsConfig.split(",")

        rackspace_templates_failed = False
        custom_templates_failed = False
        stacks_check_failed = False

        for region in regions:
            try:
                self.check_rackspace_templates(region)
            except AssertionError:
                print "** Error: Compliance check on rackspace templates has failed."
                rackspace_templates_failed = True

            try:
                self.check_custom_templates(region)
            except AssertionError, msg:
                print "** Error: Compliance check on custom templates has failed: %s" % msg
                custom_templates_failed = True

            try:
                self.check_stacks_metadata(region)
            except AssertionError:
                print "** Error: Compliance check on stacks metadata has failed."
                stacks_check_failed = True

        if rackspace_templates_failed or custom_templates_failed or stacks_check_failed:
            self.fail("Reach compatiblity tests have failed:"
                      "\n\t\t\trackspace_templates_failed:%s"
                      "\n\t\t\tcustom_templates_failed:%s"
                      "\n\t\t\tstacks_check_failed:%s" % (rackspace_templates_failed, custom_templates_failed, stacks_check_failed))

    def check_rackspace_templates(self, region):
        print "\nChecking Reach compatiblity of the rackspace-orchestration-templates..."
        resp, body = self.orchestration_client.get_rax_templates_with_metadata(region=region)
        self.assertEqual(resp['status'], '200', "expected response was 200 "
                                            "but actual was %s. Body %s" % (resp['status'], body))
        expected_template_keys = ["description", "parameters", "parameter_groups", "rackspace-metadata"]
        expected_rackspace_metadata = ["abstract", "reach-info", "description", "application-family"]
        expected_reach_info = ["tattoo", "icon-20x20"]

        template_key_error = False
        rackspace_metadata_key_error = False

        for template in body['templates']:
            template_keys = template.keys()
            for expected_template_key in expected_template_keys:
                try:
                    self.assertTrue(expected_template_key in template_keys, "Key not found in template %s: %s" % (template['id'], expected_template_key))
                except AssertionError:
                    print "** Error: Template key \"%s\" was not present. templateID=%s" % (expected_template_key, template['id'])
                    template_key_error = True

            # Now check the meta data
            rackspace_metadata = template['rackspace-metadata']

            for expected_metadata_key in expected_rackspace_metadata:
                try:
                    self.assertTrue(expected_metadata_key in rackspace_metadata.keys(), "rackspace-metadata not found in template %s: %s" % (template['id'], expected_metadata_key))
                except AssertionError:
                    print "** Error: rackspace-metadata key \"%s\" was not present. templateID=%s" % (expected_metadata_key, template['id'])
                    rackspace_metadata_key_error = True
            reach_info = rackspace_metadata['reach-info']
            for item in expected_reach_info:
                try:
                    self.assertTrue(item in reach_info.keys(), "reach-info %s not found in template %s." % (item, template['id']))
                except AssertionError:
                    print "** Error: reach-info metadata \"%s\" was not present. templateID=%s" % (item, template['id'])
                    rackspace_metadata_key_error = True

        if template_key_error or rackspace_metadata_key_error:
            self.fail("Rackspace template check failed: template_key_error:%s, rackspace_metadata_key_error:%s" % (template_key_error,rackspace_metadata_key_error))

    def check_custom_templates(self, region):
        print "\nChecking Reach compatiblity of custom templates..."

        metadata_key = "rackspace-metadata"
        template_key = "template"
        expected_template_keys = ["heat_template_version", "description", template_key, metadata_key]
        expected_rackspace_metadata = ["custom-template"]

        template = {"heat_template_version": "2013-05-23", "description": "Simple template to deploy a single compute instance", "resources": {"my_instance": {"type": "OS::Nova::Server", "properties": {"key_name": "primkey", "image": "CentOS 6.5", "flavor": "m1.small"}}}}

        # Create a custom template and post it (in case none are present)
        parameters = {}
        stack_name = rand_name("fusion_"+region)
        resp, body = self.orchestration_client.store_stack_fusion(
            stack_name, region, template=template, parameters=parameters)
        self.assertIn(resp['status'], ['200', '201'])
        template_id = body['template_id']
        print "New template stored. ID = " + str(template_id)

        # Verify existance of posted template and expected meta attributes
        print "Checking for metadata in new custom template..."
        sresp, sbody = self.orchestration_client.get_single_template_with_metadata(template_id, region)

        try:
            self.assertEqual('200', sresp['status'], "Response to get should be 200")
            self.assertTrue(template_key in sbody.keys(), "Key not found in template %s: %s" % (template_id, template_key))
            self.assertNotEqual(template, sbody[template_key], "Template we posted was equal to the one posted (returned version should have metadata)")
            self.assertTrue(metadata_key in sbody.keys(), "Key not found in template %s: %s" % (template_id, metadata_key))
            rackspace_meta_data = sbody[metadata_key]
            for data in expected_rackspace_metadata:
                self.assertTrue(data in rackspace_meta_data.keys(), "rackspace_meta_data \"%s\" not found in template %s" % (data, template_id))

            # Check for metadata in api call for all custom templates with metadata
            print "Checking for metadata in all current custom templates..."
            aresp, abody = self.orchestration_client.get_custom_templates_with_metadata(region)
            for template in abody['templates']:
                print "Checking template %s..." % template['id']
                template_keys = template.keys()
                for expected_template_key in expected_template_keys:
                    self.assertTrue(expected_template_key in template_keys, "Key \"%s\" not found in template %s" % (expected_template_key, template['id']))

                # Now check the meta data
                rackspace_meta_data = template[metadata_key]

                for data in expected_rackspace_metadata:
                    self.assertTrue(data in rackspace_meta_data.keys(), "rackspace_meta_data \"%s\" not found in template %s" % (data, template['id']))

        except AssertionError, msg:
            self.fail(msg)
        finally:
            print "Deleting template ID=%s..." % template_id
            dresp, dbody = self.orchestration_client.delete_template(template_id, region)
            self.assertEqual('200', dresp['status'], "Body %s" % dbody)
            #verify non-existence
            gresp, gbody = self.orchestration_client.get_template(template_id, region)
            self.assertEqual('404', gresp['status'], "Body %s" % gbody)

    def check_stacks_metadata(self, region):
        print "\nChecking Reach compatiblity of stacks metadata..."

        template_id = "lamp"
        #template_id = "wordpress-single"
        #template_id = "wordpress-multi"
        #template_id = "ansible-tower"

        parameters = {}
        stack_name = rand_name("fusion_"+template_id+region)
        resp, body = self.orchestration_client.create_stack_fusion(
            name=stack_name, region=region, template_id=template_id,
            parameters=parameters)
        self.assertEqual(resp['status'], '201', "expected response was 201 on create stack "
                                                "but actual was %s. Body: %s" % (resp['status'], body))

        stack_identifier = body['stack']['id']

        expected_stack_keys = ['stack_name','stack_status','stack_status_reason','creation_time','updated_time','template_id',
                               'application_name','application_version','outputs','rackspace_template','is_checkmate_migrated',
                               'rackspace-metadata']
        expected_resource_keys = ['resource_name','resource_type','resource_status','resource_status_reason','physical_resource_id','links']

        url = "stacks/%s/%s?with_support_info=1" % (stack_name, stack_identifier)
        resp, body = self.orchestration_client.get_stack_info_for_fusion(url, region)
        if resp['status'] == '200':
            # For 'outputs', we need to wait for stack creation to complete
            count = 0
            while body['stack']['stack_status'] == 'CREATE_IN_PROGRESS' and count < 20:
                print "Deployment in %s status. Checking again in 1 minute" % body['stack']['stack_status']
                time.sleep(60)
                count += 1
                resp, body = self.orchestration_client.get_stack_info_for_fusion(url, region)
                if resp['status'] == '200':
                    if body['stack']['stack_status'] == 'CREATE_FAILED':
                        print "Stack create failed. Here's why: %s" % body['stack']['stack_status_reason']
                    if count == 20:
                        print "Stack create has taken over 20 minutes. Deleting " \
                              "attempted stack for %s" % template_id
                        self._delete_stack(stack_name, stack_identifier, region)
                else:
                    print "Something went wrong. Here's what: %s, %s" % (resp, body)
        else:
            print "Something went wrong. Here's what: %s, %s" % (resp, body)
            self.fail("Something went wrong. Here's what: %s, %s" % (resp,body))

        stack = body['stack']
        if stack['stack_status'] == 'CREATE_COMPLETE':
            # block in exception handler so if a test fails in the assertion we can still cleanup in the 'finally' block
            resource_key_error = False
            stack_key_error = False
            for key in expected_stack_keys:
                try:
                    self.assertTrue(key in stack.keys(), "Stack key \"%s\" not present. id=%s, application_name=%s" % (key, stack['id'], stack['application_name']))
                except AssertionError:
                    print "** Error: Stack key \"%s\" was not present. id=%s, application_name=%s" % (key, stack['id'], stack['application_name'])
                    stack_key_error = True
            # Check the expected attributes of the resources associated with this stack
            rresp, rbody = self.orchestration_client.list_resources(stack['stack_name'], stack['id'], region)
            for resource in rbody:
                for key in expected_resource_keys:
                    try:
                        self.assertTrue(key in resource.keys(), "Resource key \"%s\" not present for stack=%s, resource=%s" % (key, stack_name, resource['resource_type']))
                        if key not in resource.keys():
                            print "** Error: Resource key \"%s\" was not present for stack=%s, resource=%s" % (key, stack_name,resource['resource_type'])
                    except AssertionError:
                        print "** Error: Resource key \"%s\" was not present for stack=%s, resource=%s" % (key, stack_name,resource['resource_type'])
                        resource_key_error = True

        dresp, dbody = self.delete_stack(stack_name, stack_identifier, region)
        if resource_key_error or stack_key_error:
            self.fail("Stacks metadata check failed: stack_key_error:%s, resource_key_error:%s" % (stack_key_error,resource_key_error))



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

