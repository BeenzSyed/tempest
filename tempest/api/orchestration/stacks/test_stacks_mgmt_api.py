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
import re


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
        usertype = self.config.identity['username']
        print "User is: %s" % usertype
        print "Environment is %s" % env

        #using urllib2
        # req = urllib2.urlopen("https://github.rackspace.com/Heat/cookbook-heat/raw/master/files/default/policy.json")
        # policy_details = yaml.load(req)
        # print policy_details

        #print "request is: %s" % req
        #html = req.read()
        #print "html is %s" % html
        #print type(html)
        #policy_details = yaml.load(html.content)

        #using requests
        # policy_file = "https://github.rackspace.com/Heat/cookbook-heat/raw/master/files/default/policy.json"
        # headers = {'Authorization': '64b66eca6f1b3f6871196d2c335dd174ce7da99d'}
        # policy = requests.post(policy_file, headers=headers, timeout=10)
        # if policy.status_code != requests.codes.ok:
        #     print "This file does not exist: %s" % policy_file
        #     self.fail("The policy file does not exist.")
        # else:
        #     policy_details = yaml.safe_load(policy.content)
        #     print policy_details

        #when I have access to github.rackspace.com
        #super_user = policy_details['allow_management_api_user'].split(":")[2]

        super_user = "heatdev"
        if usertype == super_user:
            print "%s is a super user." % (usertype)
        else:
            print "%s is a normal user." % (usertype)

        regionsConfig = self.config.orchestration['regions']
        regions = regionsConfig.split(",")[0]
        #for region in regions:
        print "\nRegion is: %s" % regions

        #stack-list
        apiname = "stack list"
        slresp, stacklist = self.orchestration_client.list_stacks(regions)
        numstacks = 0
        for stack in stacklist:
            numstacks = numstacks+1

        apiname = "stack list mgmt api"
        slrespm, stacklistm = self.orchestration_client.list_stacks_mgmt_api(regions)
        numstacksmgmt = 0
        for stack in stacklistm:
            numstacksmgmt = numstacksmgmt+1

        if usertype == super_user:
            if slrespm['status'] == '200':
                if (numstacksmgmt >= numstacks):
                    print "Management api is working! Stack list gives back %s stacks and the management api gives back %s stacks." % (numstacks, numstacksmgmt)
                else:
                    print "Management api is not working. Stack list gives back %s stacks and the management api gives back %s stacks." % (numstacks, numstacksmgmt)
                    self.fail("Management api is not working.")
            elif re.search('40*', slrespm['status']):
                print "%s does not have access. Error: %s" % (usertype, stacklistm)
                self.fail("Heatdev is a superuser and should have access.")
        else:
            if re.search('40*', slrespm['status']):
                print "%s is not a superuser and does not have access." % (usertype)
            else:
                print "%s is not a superuser and has access." % (usertype)
                self.fail("Something is wrong! A normal user has superuser access.")

    def _get_stacks(self, typestack, body):
        for stackname in body:
            match = re.search(typestack + '_*', stackname['stack_name'])
            if match:
                return stackname['stack_name'], stackname['id']
        return 0, 0

    def _get_event_id(self, body):
        for stackname in body:
            return stackname['id']




