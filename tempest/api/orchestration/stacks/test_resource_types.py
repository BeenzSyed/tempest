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
import os
import ast


LOG = logging.getLogger(__name__)

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
        self.verify_resources(body)
        print "Lists matched."

    def verify_resources(self, resources_returned):
        returned_list = resources_returned['resource_types']
        expected_list = [
            'AWS::CloudFormation::WaitCondition',
            'AWS::CloudFormation::WaitConditionHandle',
            'AWS::EC2::Instance',
            'AWS::ElasticLoadBalancing::LoadBalancer',
            'DockerInc::Docker::Container',
            'OS::Cinder::Volume',
            'OS::Cinder::VolumeAttachment',
            'OS::Heat::ChefSolo',
            'OS::Heat::CloudConfig',
            'OS::Heat::MultipartMime',
            'OS::Heat::None',
            'OS::Heat::RandomString',
            'OS::Heat::ResourceGroup',
            'OS::Heat::SoftwareConfig',
            'OS::Heat::SoftwareDeployment',
            'OS::Heat::SoftwareDeploymentGroup',
            'OS::Heat::SoftwareDeployments',
            'OS::Heat::Stack',
            'OS::Heat::SwiftSignal',
            'OS::Heat::SwiftSignalHandle',
            'OS::Neutron::Net',
            'OS::Neutron::Port',
            'OS::Neutron::SecurityGroup',
            'OS::Neutron::Subnet',
            'OS::Nova::KeyPair',
            'OS::Nova::Server',
            'OS::Swift::Container',
            'OS::Trove::Instance',
            'OS::Zaqar::Queue',
            'Rackspace::AutoScale::Group',
            'Rackspace::AutoScale::ScalingPolicy',
            'Rackspace::AutoScale::WebHook',
            'Rackspace::Cloud::BackupConfig',
            'Rackspace::Cloud::BigData',
            'Rackspace::Cloud::ChefSolo',
            'Rackspace::Cloud::CloudFilesCDN',
            'Rackspace::Cloud::DNS',
            'Rackspace::Cloud::LoadBalancer',
            'Rackspace::Cloud::Network',
            'Rackspace::Cloud::Server',
            'Rackspace::Cloud::WinServer',
            'Rackspace::CloudMonitoring::AgentToken',
            'Rackspace::CloudMonitoring::Alarm',
            'Rackspace::CloudMonitoring::Check',
            'Rackspace::CloudMonitoring::Entity',
            'Rackspace::CloudMonitoring::Notification',
            'Rackspace::CloudMonitoring::NotificationPlan',
            'Rackspace::CloudMonitoring::PlanNotifications',
            'Rackspace::Neutron::SecurityGroupAttachment',
            'Rackspace::RackConnect::PoolNode',
            'Rackspace::RackConnect::PublicIP',
        ]

        print "Making sure returned list matches\n" + '\n'.join(expected_list)
        self.assertEqual(set(returned_list) ^ set(expected_list),
                         set([]),
                         "Resource list has differences from expected")

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
