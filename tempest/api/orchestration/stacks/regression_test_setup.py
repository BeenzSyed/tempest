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
import re
import time
from testconfig import config
from datetime import datetime

import ipdb

LOG = logging.getLogger(__name__)

class RegressionTestSetup(base.BaseOrchestrationTest):
    fail_flag = 0

    @classmethod
    def setUpClass(cls):
        super(RegressionTestSetup, cls).setUpClass()
        cls.client = cls.orchestration_client

    def createPrerequisiteStacks(self, template=None):
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
            template_giturl = "https://raw.githubusercontent.com/heat-ci/heat-templates/master/prod/kitchen_sink.template"

        response_templates = requests.get(template_giturl, timeout=3)
        yaml_template = yaml.safe_load(response_templates.content)

        parameters = {}
        if 'database_name' in yaml_template['parameters']:
            parameters['database_name'] = 'wordpress_non_default_db_name'
        else:
            self.fail("Referenced template is missing parameter database_name.")

        region = "Staging"

        usertype = self.config.identity['username']
        print "User is: %s" % usertype

        # #-------  Create Prerequisite Stacks  --------------

        ipdb.set_trace()
        create_stack_name = "CREATE_%s" %datetime.now().microsecond
        csresp, csbody, csid = self.create_stack(create_stack_name, region, yaml_template, parameters)

        update_stack_name = "UPDATE_%s" %datetime.now().microsecond
        usresp, usbody, usid = self.create_stack(update_stack_name, region, yaml_template, parameters)

        adopt_stack_name = "ADOPT_%s" %datetime.now().microsecond
        asresp, asbody, asid = self.create_stack(adopt_stack_name, region, yaml_template, parameters)

        # #-------  Wait for completed creation  --------------
        ipdb.set_trace()

        self._wait_for_create(csid, region)
        self._wait_for_create(usid, region)
        self._wait_for_create(asid, region, True)


    def _wait_for_create(self, stack_id, region, check_status=False):
        sleep_count=0
        pf=0
        resp, body = self.get_stack(stack_id, region)
        if resp['status'] != '200':
            print "The response is: %s" % resp
            self.fail(resp)
        while body['stack_status'] == 'CREATE_IN_PROGRESS' and sleep_count < 90:
            print "Deployment in %s status. Checking again in 1 minute" % body['stack_status']
            time.sleep(60)
            sleep_count += 1
            resp, body = self.get_stack(stack_id, region)
            if resp['status'] != '200':
                print "The response is: %s" % resp
                self.fail(resp)
            elif sleep_count == 90:
                print "Stack create has taken over 90 minutes. Force failing now."
                self.fail(resp)
        ipdb.set_trace()
        if check_status:
            if body['stack_status'] == 'CREATE_FAILED':
                print "Stack create failed. Here's why: %s" % body['stack_status_reason']
                self.fail(resp)

