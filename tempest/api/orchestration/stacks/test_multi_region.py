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
from datetime import datetime
from tempest.test import attr
import yaml
import time
import os
import re
import pdb
import requests
from testconfig import config
import paramiko

LOG = logging.getLogger(__name__)

#0 if no failures occur, adds 1 every time a stack fails
global_pf = 0


class StacksTestJSON(base.BaseOrchestrationTest):
    _interface = 'json'

    @classmethod
    def setUpClass(cls):
        super(StacksTestJSON, cls).setUpClass()
        cls.client = cls.orchestration_client

    def test_all(self):
        self._test_stack()

    @attr(type='smoke')
    def _test_stack(self, template=None, image=None):

        print os.environ.get('TEMPEST_CONFIG')
        if os.environ.get('TEMPEST_CONFIG') == None:
            print "Set the environment varible TEMPEST_CONFIG to a config file."
            self.fail("Environment variable is not set.")

        env = self.config.orchestration['env']
        account = self.config.identity['username']

        if template == None:
            template_giturl = config['template_url']
            template = template_giturl.split("/")[-1].split(".")[0]
            print "template is %s" % template
        else:
            template_giturl = "https://raw.githubusercontent.com/heat-ci/heat-templates/master/"+env+"/"+template+".template"

        response_templates = requests.get(template_giturl, timeout=10)
        if response_templates.status_code != requests.codes.ok:
            print "This template does not exist: %s" % template_giturl
            self.fail("The template does not exist.")
        else:
            yaml_template = yaml.safe_load(response_templates.content)

        #0 if no failures occur, adds 1 every time a stack fails
        #global global_pf

        regionsConfig = self.config.orchestration['regions']


        #regions = ['DFW', 'ORD', 'IAD', 'SYD', 'HKG']
        regions = regionsConfig.split(",")
        #regions = regions_temp.split(",")
        for region in regions:

            respbi, bodybi = self.orchestration_client.get_build_info(region)
            print "\nThe build info is: %s\n" % bodybi

            stack_name = rand_name("qe_"+template+region)
            domain = "iloveheat%s.com" %datetime.now().microsecond
            #params = self._set_parameters(yaml_template, template, region, image, domain)

            print "\nDeploying %s in %s using account %s" % (template, region, account)
            csresp, csbody, stack_identifier = self.create_stack(stack_name, region, yaml_template)

            if stack_identifier == 0:
                print "Stack create failed. Here's why: %s, %s" % (csresp, csbody)
                self.fail("Stack build failed.")
            else:
                stack_id = stack_identifier.split('/')[1]
                print "Stack ID is: %s" % stack_id
                count = 0
                retry = 0

                should_restart = True
                while should_restart:
                    resp, body = self.get_stack(stack_id, region)
                    #pdb.set_trace()
                    global global_pf

                    if body['stack_status'] == 'CREATE_IN_PROGRESS' and count < 90:
                        print "Deployment in %s status. Checking again in 1 minute" % body['stack_status']
                        time.sleep(60)
                        count += 1
                    elif body['stack_status'] == 'CREATE_IN_PROGRESS' and count == 90:
                        print "Stack create has taken over 90 minutes. Force failing now."
                        self._send_deploy_time_graphite(env, region, template, count, "failtime")
                        #global global_pf
                        #global_pf += 1
                        should_restart = False
                    elif body['stack_status'] == 'CREATE_FAILED' and retry < 4:
                        print "Stack create failed. Here's why: %s" % body['stack_status_reason']
                        ssresp, ssbody = self.orchestration_client.show_stack(stack_name, stack_id, region)
                        print "Stack show output: %s" % ssbody
                        rlresp, rlbody = self.orchestration_client.list_resources(stack_name, stack_id, region)
                        print "Resource list: %s" % rlbody
                        elresp, elbody = self.orchestration_client.list_events(stack_name, stack_id, region)
                        print "Event list: %s" % elbody
                        #print "Deleting stack now"
                        self._delete_stack(stack_name, stack_id, region)
                    elif body['stack_status'] == 'CREATE_COMPLETE':
                            print "The deployment took %s minutes" % count
                            should_restart = False

                            ssresp, ssbody = self.orchestration_client.list_stacks(region)
                            if str(stack_name) + "/" in str(ssbody):
                                print "Base stack %s from multi-region exists" % stack_name
                                #including / so it doesn't accidentally match the
                                #-DFW_stack one in case they're in the same region
                            else:
                                print "Base stack %s for multi-region does not exist" % stack_name
                                global_pf += 1

                            for reg in regions:
                                regssresp, regssbody = self.orchestration_client.list_stacks(str(reg))
                                stack_name_reg = str(stack_name) + "-" + str(reg) + "_stack-"

                                if stack_name_reg in str(regssbody):
                                    print "Secondary stack %s************ in multi-region (%s) exists" % (stack_name_reg, reg)
                                else:
                                    print "Secondary stack %s************ in multi-region (%s) does not exist" % (stack_name_reg, reg)
                                    global_pf += 1

                            self._delete_stack(stack_name, stack_id, region)

                    else:
                        print "This stack is crazy"

        if global_pf > 0:
            self.fail("Looks like %s stacks failed to build." % global_pf)

    def _delete_stack(self, stack_name, stack_id, region):
        print "Deleting stack now"
        resp_delete, body_delete = self.delete_stack(stack_name, stack_id, region)
        if resp_delete['status'] == '204':
            print "Delete request sent"
        else:
            print resp_delete['status']
            print "Something went wrong during the delete call"



