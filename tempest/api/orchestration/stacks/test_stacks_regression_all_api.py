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
from tempest.openstack.common import log as logging
from tempest.test import attr
import requests
import yaml
import os


LOG = logging.getLogger(__name__)


class StacksTestJSON(base.BaseOrchestrationTest):
    _interface = 'json'

    empty_template = "HeatTemplateFormatVersion: '2013-05-23'\n"

    @classmethod
    def setUpClass(cls):
        super(StacksTestJSON, cls).setUpClass()
        cls.client = cls.orchestration_client

    def test_devstack_realDeployment(self):
        self._test_stack("devstack")

    def test_dotnetnuke_realDeployment(self):
        self._test_stack("dotnetnuke")

    def test_mongodb_realDeployment(self):
        self._test_stack("mongodb")

    def test_mysql_realDeployment(self):
        self._test_stack("mysql")

    def test_php_app_realDeployment(self):
        self._test_stack("php-app")

    def test_rcbops_realDeployment(self):
        self._test_stack("rcbops_allinone_inone")

    def test_redis_realDeployment(self):
        self._test_stack("redis")

    def test_repose_realDeployment(self):
        self._test_stack("repose")

    def test_ruby_on_rails_realDeployment(self):
        self._test_stack("ruby-on-rails")

    def test_wordpress_multi_realDeployment(self):
        self._test_stack("wordpress-multi")

    def test_wordpress_multi_windows_realDeployment(self):
        self._test_stack("wordpress-multinode-windows")

    def test_wordpress_single_winserver_realDeployment(self):
        self._test_stack("wordpress-single-winserver")

    def test_wordpress_winserver_clouddb_realDeployment(self):
        self._test_stack("wordpress-winserver-clouddb")

    def test_wp_resource_realDeployment(self):
        self._test_stack("wp-resource")

    def test_wp_single_linux_realDeployment(self):
        self._test_stack("wp-single-linux-cdb")

    def test_rackconnect_realDeployment(self):
        self._test_stack("php-app")

    @attr(type='smoke')
    def _test_stack(self, template):
        print os.environ.get('TEMPEST_CONFIG')

        env = self.config.orchestration['env']
        template_giturl = "https://raw2.github.com/heat-ci/heat-templates/master/" + env + "/" + template + ".template"
        #print template_giturl
        response_templates = requests.get(template_giturl, timeout=3)
        yaml_template = yaml.safe_load(response_templates.content)
        #print yaml_template

        parameters = {}
        if 'key_name' in yaml_template['parameters']:
            parameters = {
                'key_name': 'sabeen'
            }
        if 'git_url' in yaml_template['parameters']:
            parameters['git_url'] = "https://github.com/timductive/phphelloworld"
            #https://github.com/beenzsyed/phphelloworld

        #print parameters
        stack_id = "77e36391-6494-4d69-9bca-a1f86ba81004"
        stack_name = "qe_devstackDev-tempest-729419543"
        region = "Dev"
        rstype = "Rackspace::Cloud::Server"
        rsname = "devstack_server"
        event_id = '97bd2404-bb1a-45ff-afc0-c73299562426'

        #update stack
        # print "update stack"
        # usresp, usbody = self.orchestration_client.update_stack(stack_id, region, "sabeenlovesheat", yaml_template, parameters)
        # self._check_resp(usresp, usbody, "update stack")

        #-------  Stacks  --------------
        #create stack
        #print "create stack"
        ssresp, ssbody = self.orchestration_client.create_stack("isthisworking", region, yaml_template, parameters)
        self._check_resp(ssresp, ssbody, "create stack")

        #update stack
        #print "update stack"
        ssresp, ssbody = self.orchestration_client.update_stack(stack_id, stack_name, region, yaml_template, parameters)
        self._check_resp(ssresp, ssbody, "update stack")

        #stack show
        #print "show stack"
        ssresp, ssbody = self.orchestration_client.show_stack(stack_name, stack_id, region)
        self._check_resp(ssresp, ssbody, "show stack")

        #stack-list
        #print "stack list"
        slresp, slbody = self.orchestration_client.list_stacks(region)
        self._check_resp(slresp, slbody, "stack list")

        #delete stack
        #print "delete stack"
        ssresp, ssbody = self.orchestration_client.delete_stack(stack_name, stack_id, region)
        self._check_resp(ssresp, ssbody, "delete stack")

        #abandon stack
        #print "abandon stack"
        asresp, asbody, = self.orchestration_client.abandon_stack(stack_name, stack_id, region)
        self._check_resp(asresp, asbody, "abandon stack")

        #adopt stack
        #print "adopt stack"
        asresp, asbody, = self.orchestration_client.abandon_stack(stack_name, stack_id, region)
        self._check_resp(asresp, asbody, "adopt stack")


        #-------  Stack events  ----------
        #event list
        #print "event list"
        evresp, evbody = self.orchestration_client.list_events(stack_name, stack_id, region)
        self._check_resp(evresp, evbody, "event list")

        #event show
        #print "event show"
        esresp, esbody = self.orchestration_client.show_event(stack_name, stack_id, rsname, event_id, region)
        self._check_resp(esresp, esbody, "event show")


        #-------  Templates  -------------
        #template show
        #print "template show"
        tsresp, tsbody = self.orchestration_client.show_template(stack_name, stack_id, region)
        self._check_resp(tsresp, tsbody, "template show")

        #template validate
        #print "template validate"
        tvresp, tvbody = self.orchestration_client.validate_template(region, yaml_template, parameters)
        self._check_resp(tvresp, tvbody, "template validate")


        #--------  Stack resources  --------
        #Lists resources in a stack.
        #print "list resources"
        lrresp, lrbody = self.orchestration_client.list_resources(stack_name, stack_id, region)
        self._check_resp(lrresp, lrbody, "list resources")

        #Gets metadata for a specified resource.
        #print "resource metadata"
        rmresp, rmbody = self.orchestration_client.show_resource_metadata(stack_name, stack_id, rsname, region)
        self._check_resp(rmresp, rmbody, "resource metadata")

        #Gets data for a specified resource.
        #print "get resources"
        rsresp, rsbody = self.orchestration_client.get_resource(stack_name, stack_id, rsname, region)
        self._check_resp(rsresp, rsbody, "get resources")

        #Gets a template representation for a specified resource type.
        #print "resource template"
        rtresp, rtbody = self.orchestration_client.resource_template(rstype, region)
        self._check_resp(rtresp, rtbody, "resource template")

        #Lists the supported template resource types.
        rtresp, rtbody = self.orchestration_client.template_resource(region)
        self._check_resp(rtresp, rtbody, "template resource types")

        #Gets the interface schema for a specified resource type.
        rtresp, rtbody = self.orchestration_client.resource_schema(rstype, region)
        self._check_resp(rtresp, rtbody, "schema for resource type")


        # #suspend stack, wait 1 min
        # print "suspend stack"
        # ssresp, ssbody = self.orchestration_client.suspend_stack(stack_name, region)
        # self._check_resp(ssresp, ssbody, "suspend stack")
        #
        # time.sleep(60)
        #
        # #resume stack
        # print "resume stack"
        # rsresp, rsbody = self.client.resume_stack(stack_id, region)
        # self._check_resp(rsresp, rsbody, "resume stack")

        #pf is the variable that stays 0 if no failures occur, turns to 1 if a build fails
        pf = 0

        # regionsConfig = self.config.orchestration['regions']
        # #regions = ['DFW', 'ORD', 'IAD', 'SYD', 'HKG']
        # regions = regionsConfig.split(",")
        # for region in regions:
        #     stack_name = rand_name("qe_"+template+region)
        #     parameters = {}
        #     if 'key_name' in yaml_template['parameters']:
        #         parameters = {
        #             'key_name': 'sabeen'
        #         }
        #     if 'git_url' in yaml_template['parameters']:
        #         parameters['git_url'] = "https://github.com/timductive/phphelloworld"
        #
        #     print "\nDeploying %s in %s" % (template, region)
        #     stack_identifier = self.create_stack(stack_name, region, yaml_template, parameters)
        #     stack_id = stack_identifier.split('/')[1]
        #     count = 0
        #     resp, body = self.get_stack(stack_id, region)
        #     print "Stack %s status is: %s, %s" % (stack_name, body['stack_status'], body['stack_status_reason'])
        #
        #     while body['stack_status'] == 'CREATE_IN_PROGRESS' and count < 90:
        #         resp, body = self.get_stack(stack_id, region)
        #         if resp['status'] != '200':
        #             print "The response is: %s" % resp
        #             self.fail(resp)
        #         print "Deployment in %s status. Checking again in 1 minute" % body['stack_status']
        #         time.sleep(60)
        #         count += 1
        #         if body['stack_status'] == 'CREATE_FAILED':
        #             print "Stack create failed. Here's why: %s" % body['stack_status_reason']
        #             self._send_deploy_time_graphite(env, region, template, count, "failtime")
        #             if os.environ.get('TEMPEST_CONFIG') == "tempest_qa.conf":
        #                 print "Deleting the stack now"
        #                 dresp, dbody = self.delete_stack(stack_name, stack_id)
        #                 if dresp['status'] != '204':
        #                     print "Delete did not work"
        #             pf += 1
        #         elif count == 90:
        #             print "Stack create has taken over 90 minutes. Force failing now."
        #             self._send_deploy_time_graphite(env, region, template, count, "failtime")
        #             if os.environ.get('TEMPEST_CONFIG') == "tempest_qa.conf":
        #                 print "Stack create took too long. Deleting stack now."
        #                 dresp, dbody = self.delete_stack(stack_name, stack_id)
        #                 if dresp['status'] != '204':
        #                     print "Delete did not work"
        #             pf += 1
        #
        #     if body['stack_status'] == 'CREATE_COMPLETE':
        #         print "The deployment took %s minutes" % count
        #         self._send_deploy_time_graphite(env, region, template, count, "buildtime")
        #         #extract region and name of template
        #
        #         #suspend stack, wait 1 min
        #         print "suspend stack"
        #         ssresp, ssbody = self.orchestration_client.suspend_stack(stack_id)
        #         self._check_resp(ssresp, ssbody, "suspend stack")
        #
        #         #delete stack
        #         print "Deleting stack now"
        #         resp, body = self.delete_stack(stack_name, stack_id)
        #         if resp['status'] != '204':
        #             print "Delete did not work"
        #
        #     else:
        #         print "Something went wrong! This could be the reason: %s" % body['stack_status_reason']
        #         self.fail("Stack build failed.")
        #
        # if pf > 0:
        #     self.fail("Stack build failed.")

    def _send_deploy_time_graphite(self, env, region, template, deploy_time, buildfail):
        cmd = 'echo "heat.' + env + '.build-tests.' + region + '.' + template \
              + '.' + buildfail + '  ' + str(deploy_time) \
              + ' `date +%s`" | ' \
                'nc graphite.staging.rs-heat.com ' \
                '2003 -q 2'
        #print cmd
        os.system(cmd)
        print "Deploy time sent to graphite"

    def _check_resp(self, resp, body, apiname):
        if resp['status'] == '200':
            print "%s worked! The response is: %s" % (apiname, resp['status'])
            #print "%s worked! The response is: %s The info you need is: %s" % (apiname, resp, body)
        else:
            print "%s did not work. The response is: %s" % (apiname, resp['status'])
            #print "%s did not work. The response is: %s" % (apiname, resp)
