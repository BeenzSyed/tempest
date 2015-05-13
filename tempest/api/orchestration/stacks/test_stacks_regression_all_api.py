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
import datetime
import re
from testconfig import config
from httplib import BadStatusLine

LOG = logging.getLogger(__name__)


class StacksTestJSON(base.BaseOrchestrationTest):
    _interface = 'json'

    fail_flag = 0

    empty_template = "HeatTemplateFormatVersion: '2013-05-23'\n"

    @classmethod
    def setUpClass(cls):
        super(StacksTestJSON, cls).setUpClass()
        cls.client = cls.orchestration_client

    def test_devstack_realDeployment(self):
        self._test_stack("devstack")

    def test_all(self):
        self._test_stack()

    @attr(type='smoke')
    def _test_stack(self, template=None):

        print os.environ.get('TEMPEST_CONFIG')
        if os.environ.get('TEMPEST_CONFIG') == None:
            print "Set the environment varible TEMPEST_CONFIG to a config file."
            self.fail("Environment variable is not set.")

        env = self.config.orchestration['env']
        account = self.config.identity['username']

        print template

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

        parameters = {}
        if 'key_name' in yaml_template['parameters']:
            parameters = {
                'key_name': 'sabeen'
            }
        if 'git_url' in yaml_template['parameters']:
            parameters['git_url'] = "https://github.com/timductive/phphelloworld"

        usertype = self.config.identity['username']
        print "User is: %s" % usertype
        print "Environment is %s" % env
        regionsConfig = self.config.orchestration['regions']
        #regions = ['DFW', 'ORD', 'IAD', 'SYD', 'HKG']
        regions = regionsConfig.split(",")
        for region in regions:
            print "\nRegion is: %s" % region

            # #-------  Stacks  --------------
            #stack-list
            apiname = "stack list"
            slresp, stacklist = self.orchestration_client.list_stacks(region)
            self._check_resp(slresp, stacklist, apiname)

            #create stack
            apiname = "create stack"
            create_stack_name = "CREATE_%s" % datetime.datetime.now().\
                microsecond
            try:
                csresp, csbody, stack_identifier = self.create_stack(
                    create_stack_name, region, yaml_template, parameters)
                self._check_resp(csresp, csbody, apiname)
            except BadStatusLine:
                print "Create stack did not work"

            #stack-list - doing this again because it has known to fail if
            # called after a stack create
            apiname = "stack list"
            slresp, stacklist = self.orchestration_client.list_stacks(region)
            self._check_resp(slresp, stacklist, apiname)

            #update stack
            apiname = "update stack"
            parameters_update = {
                    'server_hostname': 'sabeen'
            }

            updateStackName, updateStackId = self._get_stacks("UPDATE_",
                                                              stacklist,
                                                              region)
            if updateStackName != 0:
                try:
                    ssresp, ssbody = self.update_stack(updateStackId,
                                                       updateStackName, region,
                                                       yaml_template, parameters_update)
                    self._check_resp(ssresp, ssbody, apiname)
                except BadStatusLine:
                    print "Update stack did not work"

            #stack show
            apiname = "show stack"
            if updateStackName != 0:
                ssresp, ssbody = self.orchestration_client.show_stack(
                    updateStackName, updateStackId, region)
                self._check_resp(ssresp, ssbody, apiname)

            #stack preview
            apiname = "preview stack"
            if updateStackName != 0:
                spresp, spbody = self.orchestration_client.stack_preview(
                    name='preview_stack', region=region,
                    template=yaml_template)
                self._check_resp(spresp, spbody, apiname)

            #delete stack
            apiname = "delete stack"
            deleteStackName, deleteStackId = self._get_stacks("CREATE_",
                                                              stacklist,
                                                              region)
            if deleteStackName != 0:
                try:
                    ssresp, ssbody = self.orchestration_client.delete_stack(
                        deleteStackName, deleteStackId, region)
                    self._check_resp(ssresp, ssbody, apiname)
                except BadStatusLine:
                    print "Delete stack did not work"

            #abandon stack
            apiname = "abandon stack"
            abandonStackName, abandonStackId = self._get_stacks("ADOPT_",
                                                                stacklist,
                                                                region)
            if abandonStackName != 0:
                try:
                    asresp, asbody = self.abandon_stack(abandonStackId,
                                                 abandonStackName, region)
                    self._check_resp(asresp, asbody, apiname)
                except BadStatusLine:
                    print "Delete stack did not work"

                apiname = "adopt stack"

                adopt_stack_name = "ADOPT_%s" %datetime.datetime.now().microsecond
                try:
                    adresp, adbody, stack_identifier = self.adopt_stack(
                        adopt_stack_name, region, asbody, yaml_template,
                        parameters)
                    self._check_resp(adresp, adbody, apiname)
                except BadStatusLine:
                    print "Adopt stack did not work"

            #--------  Stack resources  --------
            #Lists resources in a stack
            apiname = "list resources"
            if updateStackName != 0:
                lrresp, lrbody = self.orchestration_client.list_resources(
                    updateStackName, updateStackId, region)
                self._check_resp(lrresp, lrbody, apiname)

            #Gets metadata for a specified resource.
            apiname = "resource metadata"
            if updateStackName != 0:
                rs_name = self._get_resource_name(lrbody)
                rmresp, rmbody = self.orchestration_client.\
                    show_resource_metadata(updateStackName, updateStackId,
                                           rs_name, region)
                self._check_resp(rmresp, rmbody, apiname)

            #Gets data for a specified resource.
            apiname = "get resources"
            if updateStackName != 0:
                rsresp, rsbody = self.orchestration_client.get_resource(
                    updateStackName, updateStackId, rs_name, region)
                self._check_resp(rsresp, rsbody, apiname)

            #Gets a template representation for a specified resource type.
            apiname = "resource template"
            if updateStackName != 0:
                rs_type = self._get_resource_type(lrbody)
                rtresp, rtbody = self.orchestration_client.resource_template(
                    rs_type, region)
                self._check_resp(rtresp, rtbody, apiname)

            #Lists the supported template resource types.
            apiname = "template resource types"
            rtresp, rtbody = self.orchestration_client.template_resource(
                region)
            self._check_resp(rtresp, rtbody, apiname)

            #Gets the interface schema for a specified resource type.
            apiname = "schema for resource type"
            if updateStackName != 0:
                rtresp, rtbody = self.orchestration_client.resource_schema(
                    rs_type, region)
                self._check_resp(rtresp, rtbody, apiname)


            #-------  Stack events  ----------
            #event list
            apiname = "list event"
            if updateStackName != 0:
                evresp, evbody = self.orchestration_client.list_events(
                    updateStackName, updateStackId, region)
                self._check_resp(evresp, evbody, apiname)

            #event show
            apiname = "show event"
            if updateStackName != 0:
                event_id, rs_name_event = self._get_event_id(evbody)
                esresp, esbody = self.orchestration_client.show_event(
                    updateStackName, updateStackId, rs_name_event, event_id,
                    region)
                self._check_resp(esresp, esbody, apiname)


            #-------  Templates  -------------
            #template show
            apiname = "template show"
            if updateStackName != 0:
                tsresp, tsbody = self.orchestration_client.show_template(
                    updateStackName, updateStackId, region)
                self._check_resp(tsresp, tsbody, apiname)

            #template validate
            apiname = "template validate"
            tvresp, tvbody = self.orchestration_client.validate_template(
                region, yaml_template, parameters)
            self._check_resp(tvresp, tvbody, apiname)


            #--------- Fusion -----------------
            # Get template catalog
            apiname = "fusion template catalog"
            tcresp, tcbody = self.orchestration_client.get_template_catalog(region)
            self._check_resp(tcresp, tcbody, apiname)

            # Get single template from catalog
            apiname = "fusion single template"
            template_id = "wordpress-single"
            tsresp, tsbody = self.orchestration_client.get_single_template(template_id, region)
            self._check_resp(tsresp, tsbody, apiname)

            # Get template catalog with metadata
            apiname = "fusion template catalog metadata"
            cmresp, cmbody = self.orchestration_client.get_template_catalog_with_metadata(region)
            self._check_resp(cmresp, cmbody, apiname)

            # Get single template catalog with metadata
            apiname = "fusion single catalog metadata"
            template_id = "wordpress-single"
            smresp, smbody = self.orchestration_client.get_single_template_with_metadata(template_id, region)
            self._check_resp(smresp, smbody, apiname)

        if updateStackName == 0:
            print "Create a stack named UPDATE_123 so that I can verify " \
                  "more api calls"

        if self.fail_flag == 0:
            print "All api's are up!"
        elif self.fail_flag > 0:
            print "One or more api's failed. Look above."
            self.fail("One or more api's failed.")

        # #suspend stack, wait 1 min
        # print "suspend stack"
        # ssresp, ssbody = self.orchestration_client.suspend_stack(stack_name,
        # region)
        # self._check_resp(ssresp, ssbody, "suspend stack")
        #
        # time.sleep(60)
        #
        # #resume stack
        # print "resume stack"
        # rsresp, rsbody = self.client.resume_stack(stack_id, region)
        # self._check_resp(rsresp, rsbody, "resume stack")

    def _send_deploy_time_graphite(self, env, region, template, deploy_time,
                                   buildfail):
        cmd = 'echo "heat.' + env + '.build-tests.' + region + '.' + template \
              + '.' + buildfail + '  ' + str(deploy_time) \
              + ' `date +%s`" | ' \
                'nc graphite.staging.rs-heat.com ' \
                '2003 -q 2'
        #print cmd
        os.system(cmd)
        print "Deploy time sent to graphite"

    def _check_resp(self, resp, body, apiname):
        match = re.search('5[0-9][0-9]', resp['status']) or \
            re.search('404', resp['status'])
        if match:
            print "%s did not work. The response is: %s %s" % (apiname,
                                                    resp['status'], body)
            self.fail_flag += 1
        else:
            print "%s worked! The response is: %s" % (apiname, resp['status'])
        # if resp['status'] == '200' or resp['status'] == '201' or \
        #                 resp['status']== '202' or resp['status'] == '204':
        #     print "%s worked! The response is: %s" % (apiname, resp['status'])
        # else:
        #     print "%s did not work. The response is: %s %s" % (apiname,
        #                                                        resp['status'],
        #                                                        body)

    def _get_stacks(self, typestack, body, region):

        for stackname in body:
            match = re.search(typestack + '_*', stackname['stack_name'])
            if match and (stackname['stack_status'] not in
                ['CREATE_IN_PROGRESS', 'ADOPT_FAILED',
                               'ADOPT_IN_PROGRESS', 'DELETE_FAILED']):
                #print stackname
                ssresp, ssbody = self.orchestration_client.show_stack(
                    stackname['stack_name'], stackname['id'], region)
                #print ssresp
                #print ssbody
                return stackname['stack_name'], stackname['id']
        return 0, 0

    def _get_event_id(self, body):
        for stackname in body:
            return stackname['id'], stackname['resource_name']

    def _get_resource_name(self, body):
        for resource in body:
            return resource['resource_name']

    def _get_resource_type(self, body):
        for resource in body:
            return resource['resource_type']