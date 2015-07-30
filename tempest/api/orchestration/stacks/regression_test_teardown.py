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

LOG = logging.getLogger(__name__)

class RegressionTestTearDown(base.BaseOrchestrationTest):
    fail_flag = 0

    @classmethod
    def setUpClass(cls):
        super(RegressionTestTearDown, cls).setUpClass()
        cls.client = cls.orchestration_client

    def deletePrerequisiteStacks(self):
        print os.environ.get('TEMPEST_CONFIG')
        if os.environ.get('TEMPEST_CONFIG') == None:
            print "Set the environment varible TEMPEST_CONFIG to a config file."
            self.fail("Environment variable is not set.")

        env = self.config.orchestration['env']
        account = self.config.identity['username']

        region = "Staging"

        usertype = self.config.identity['username']
        print "User is: %s" % usertype

        slresp, stacklist = self.orchestration_client.list_stacks(region)
        if stacklist:
            for stack in stacklist:
                if stack['stack_status'] != 'DELETE_IN_PROGRESS':
                    #delete stack
                    dsresp, dsbody = self.orchestration_client.delete_stack(stack['stack_name'], stack['id'], region)
        else:
            print "No stacks to delete in %s" % region

