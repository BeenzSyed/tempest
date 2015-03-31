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
from urlparse import urlparse
from tempest.common import rest_client



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
        self._check_resources()

    @attr(type='smoke')
    def _check_resources(self):

        print os.environ.get('TEMPEST_CONFIG')
        if os.environ.get('TEMPEST_CONFIG') == None:
            print "Set the environment varible TEMPEST_CONFIG to a config file."
            self.fail("Environment variable is not set.")

        env = self.config.orchestration['env']
        account = self.config.identity['username']

        #get the resource list

        resp, body = self.get_resource_types()

        #verify it





    def get_resource_types(self):
        url = "resource_types"
        region = "DFW"
        #request
        resp, body = self.orchestration_client.get(url, region)
        #making the response bad until finished implementing
        resp['status'] = '404'
        if resp['status'] == '200':
            print "Got resource type list"
        else:
            print resp['status']
            self.fail('Bad response from resource list')
            print "Something went wrong with the resource list"

        return resp, body

