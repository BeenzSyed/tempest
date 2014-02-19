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
from tempest.test import attr
import requests
import yaml
import time
import os
from path import path
import datetime

LOG = logging.getLogger(__name__)


class StacksTestJSON(base.BaseOrchestrationTest):
    _interface = 'json'


    @classmethod
    def setUpClass(cls):
        super(StacksTestJSON, cls).setUpClass()
        cls.client = cls.orchestration_client


    def test_autoscale_response(self):

        region , stack_id , stack_name =  self._create_stack()

        stack_id= stack_id
        stack_name = stack_name
        region = region
        resp,body = self.client.show_stack(stack_name,stack_id,region)
        for output in body['stack']['outputs']:
            if output['output_key'] in ('increment_url', 'decrement_url'):
                url = output['output_value']
                status = output['output_key']
                resp,body = self.client.validate_autoscale_response(url ,
                                                                    region)
                if resp['status'] == '202':
                    print "Autoscale for %s has status of 202 ", status
                else :
                    print " Fail to Autoscale the resource for %s" , status

          # Call for Delete stack
        self._delete_stack(stack_name ,stack_id ,region)
        print "Stack Deleted"

    def _create_stack(self):

        print os.environ.get('TEMPEST_CONFIG')

        template_giturl ="https://raw2.github.com/openstack/heat-templates/master/hot/RackspaceAutoScale.yaml"
        response_templates = requests.get(template_giturl, timeout=3)
        if response_templates.status_code != requests.codes.ok:
             print "This template does not exist: %s" % template_giturl
             self.fail("The template does not exist.")
        else:
             yaml_template = yaml.load(response_templates.content)

        regions = ['DFW']
        for region in regions:
            stack_name = rand_name("qe_Autoscale_"+"region_test")
            parameters = {
                'key_name': 'sabeen',
                'flavor': '5',
                'image' : 'bced783b-31d2-4637-b820-fa02522c518b'
            }

            print "\nDeploying %s in %s" % ( "Autoscale template", region)
            stack_identifier = self.create_stack(stack_name, region, yaml_template, parameters)

            if stack_identifier == 0:
                self.fail("Stack build failed.")
            else:
                stack_id = stack_identifier.split('/')[1]
                count = 0
                resp, body = self.get_stack(stack_id, region)
                if resp['status'] != '200':
                        print "The response is: %s" % resp
                        self.fail(resp)
                print "Stack %s status is: %s, %s" % (stack_name, body['stack_status'], body['stack_status_reason'])

                while body['stack_status'] == 'CREATE_IN_PROGRESS' and count < 90:
                    resp, body = self.get_stack(stack_id, region)
                    if resp['status'] != '200':
                        print "The response is: %s" % resp
                        self.fail(resp)
                    print "Deployment in %s status. Checking again in 1 minute" % body['stack_status']
                    time.sleep(60)
                    count += 1
                    if body['stack_status'] == 'CREATE_FAILED':
                        print "Stack create failed. Here's why: %s" % body['stack_status_reason']

                        if os.environ.get('TEMPEST_CONFIG') == "tempest_qa.conf":
                            print "Deleting the stack now"
                            dresp, dbody = self.delete_stack(stack_name, stack_id, region)
                            if dresp['status'] != '204':
                                print "Delete did not work"

                    elif count == 90:
                        print "Stack create has taken over 90 minutes. Force failing now."

                        if os.environ.get('TEMPEST_CONFIG') == "tempest_qa.conf":
                            print "Stack create took too long. Deleting stack now."
                            dresp, dbody = self.delete_stack(stack_name, stack_id, region)
                            if dresp['status'] != '204':
                                print "Delete did not work"

                if body['stack_status'] == 'CREATE_COMPLETE':
                    print "The deployment took %s minutes" % count
                else:
                     print "Something went wrong! This could be the reason: %s" % body['stack_status_reason']
        return (region , stack_id , stack_name)

    def _delete_stack(self, stack_name , stack_id ,region):
        #delete stack
        print "Deleting stack now"
        resp, body = self.delete_stack(stack_name, stack_id, region)
        if resp['status'] != '204':
            print "Delete did not work"

        else:
             print "Delete did not work"

        return resp

