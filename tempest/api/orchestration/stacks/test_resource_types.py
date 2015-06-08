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
        resources_expected = {}
        resource_list = ['Rackspace::Cloud::BackupConfig', "AWS::EC2::Instance", "Rackspace::RackConnect::PublicIP", "Rackspace::CloudMonitoring::Entity", "OS::Heat::SoftwareDeployment", "OS::Heat::SwiftSignal", "OS::Heat::ChefSolo", "Rackspace::Cloud::WinServer", "Rackspace::RackConnect::PoolNode", "OS::Heat::SoftwareDeployments", "AWS::CloudFormation::WaitConditionHandle", "OS::Cinder::VolumeAttachment", "OS::Trove::Instance", "OS::Heat::CloudConfig", "DockerInc::Docker::Container", "OS::Cinder::Volume", "OS::Heat::SoftwareConfig", "Rackspace::CloudMonitoring::AgentToken", "Rackspace::Cloud::LoadBalancer", "AWS::CloudFormation::WaitCondition", "Rackspace::CloudMonitoring::Alarm", "OS::Heat::SwiftSignalHandle", "OS::Neutron::Port", "OS::Heat::RandomString", "OS::Nova::KeyPair", "OS::Heat::MultipartMime", "OS::Nova::Server", "OS::Neutron::Net", "Rackspace::Cloud::ChefSolo", "Rackspace::AutoScale::WebHook", "Rackspace::CloudMonitoring::Notification", "Rackspace::Cloud::DNS", "Rackspace::Cloud::Network", "OS::Swift::Container", "Rackspace::Cloud::Server", "OS::Zaqar::Queue", "OS::Heat::Stack", "OS::Heat::ResourceGroup", "Rackspace::CloudMonitoring::Check", "Rackspace::CloudMonitoring::NotificationPlan", "OS::Neutron::Subnet", "Rackspace::CloudMonitoring::PlanNotifications", "Rackspace::AutoScale::ScalingPolicy", "AWS::ElasticLoadBalancing::LoadBalancer", "Rackspace::AutoScale::Group", "OS::Heat::SoftwareDeploymentGroup", "OS::Heat::SoftwareDeploymentGroup"]
        resources_expected["resource_types"] = resource_list
        print "Comparing list returned and expected list"
        resources_returned['resource_types'] = sorted(resources_returned['resource_types'])
        resources_expected['resource_types'] = sorted(resources_expected['resource_types'])
        if (resources_returned['resource_types'] != resources_expected['resource_types']):
            list_diff_1 = [item for item in resources_expected["resource_types"] if item not in resources_returned['resource_types']]
            list_diff_2 = [item for item in resources_returned['resource_types'] if item not in resources_expected["resource_types"]]
            print "Difference in lists: \n"
            print "Items in test list that aren't in actual list: " + str(list_diff_1)
            print "Items in actual list that aren't in test list: " + str(list_diff_2)
        self.assertEqual(resources_returned['resource_types'], resources_expected["resource_types"], "Expected resource type list does not match what we get.")
        resources_returned['eric'] = 'Eric'
        self.assertNotEqual(resources_returned['resource_types'], resources_expected, "Make sure things don't have false positives")

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