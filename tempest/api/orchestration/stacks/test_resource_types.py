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
import json
import time
import os
import re
import pdb
import requests
from testconfig import config
import paramiko
from urlparse import urlparse
from tempest.common import rest_client
import ast


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
        body = ast.literal_eval(body)

        #verify it
        if not self.verify_resources(body):
            self.fail("Expected resource type list does not match what we get.")


    def verify_resources(self, resources_returned):
        resources_expected = {}
        resource_list = ["AWS::EC2::Instance", "Rackspace::RackConnect::PublicIP", "Rackspace::CloudMonitoring::Entity", "OS::Heat::SoftwareDeployment", "OS::Heat::SwiftSignal", "OS::Heat::ChefSolo", "Rackspace::Cloud::WinServer", "Rackspace::RackConnect::PoolNode", "OS::Heat::SoftwareDeployments", "AWS::CloudFormation::WaitConditionHandle", "OS::Cinder::VolumeAttachment", "OS::Trove::Instance", "OS::Heat::CloudConfig", "DockerInc::Docker::Container", "OS::Cinder::Volume", "OS::Heat::SoftwareConfig", "Rackspace::CloudMonitoring::AgentToken", "Rackspace::Cloud::LoadBalancer", "AWS::CloudFormation::WaitCondition", "Rackspace::CloudMonitoring::Alarm", "OS::Heat::SwiftSignalHandle", "OS::Neutron::Port", "OS::Heat::RandomString", "OS::Trove::Cluster", "OS::Nova::KeyPair", "OS::Heat::MultipartMime", "OS::Nova::Server", "OS::Neutron::Net", "Rackspace::Cloud::ChefSolo", "Rackspace::AutoScale::WebHook", "Rackspace::CloudMonitoring::Notification", "Rackspace::Cloud::DNS", "Rackspace::Cloud::Network", "OS::Swift::Container", "Rackspace::Cloud::Server", "OS::Zaqar::Queue", "OS::Heat::Stack", "OS::Heat::ResourceGroup", "Rackspace::CloudMonitoring::Check", "Rackspace::CloudMonitoring::NotificationPlan", "OS::Neutron::Subnet", "Rackspace::CloudMonitoring::PlanNotifications", "Rackspace::AutoScale::ScalingPolicy", "AWS::ElasticLoadBalancing::LoadBalancer", "Rackspace::AutoScale::Group"]
        resources_expected["resource_types"] = resource_list

        return resources_returned == resources_expected



    def get_resource_types(self):
        url = "resource_types"
        region = "DFW"
        #request
        resp, body = self.orchestration_client.get(url, region)
        #making the response bad until finished implementing
        if resp['status'] == '200':
            print "Got resource type list"
        else:
            print resp['status']
            self.fail('Bad response from resource list')
            print "Something went wrong with the resource list"

        return resp, body

