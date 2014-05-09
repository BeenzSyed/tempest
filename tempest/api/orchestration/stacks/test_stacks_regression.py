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
import json
from testconfig import config
import urllib2
#from bs4 import BeautifulSoup

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

    def test_wordpress_multi_dns_realDeployment(self):
        self._test_stack("wordpress-multi-dns")

    def test_ubuntu(self):
        self._test_stack("hello-world", "ubuntu")

    def test_centos(self):
        self._test_stack("hello-world", "centos")

    def test_chef_solo(self):
        self._test_stack("chef_multi_node_wordpress")

    def test_kitchen_sink(self):
        self._test_stack("kitchen_sink")

    def test_all(self):
        self._test_stack()

    # def test_soup(self):
    #     webpage = urllib2.urlopen('https://github.com/rackspace-orchestration-templates').read()
    #     soup = BeautifulSoup(webpage)
    #     for link in soup.find_all('a'):
    #         if len((link.get('href').split('/'))) == 3 and link.get('href').split('/')[1] == "rackspace-orchestration-templates":
    #             webpage_child = urllib2.urlopen('https://github.com'+link.get('href')).read()
    #             soup_child = BeautifulSoup(webpage_child)
    #             for child_links in soup_child.find_all('a'):
    #                 searchObj = re.search(r'yaml', child_links.get('href'), re.M|re.I)
    #                 if searchObj:
    #                     final_link = "https://raw.githubusercontent.com"+child_links.get('href')
    #                     print final_link.replace("blob/", "")

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
        pf = 0

        regionsConfig = self.config.orchestration['regions']
        #regions = ['DFW', 'ORD', 'IAD', 'SYD', 'HKG']
        regions = regionsConfig.split(",")
        for region in regions:
            stack_name = rand_name("qe_"+template+region)
            domain_name = "example%s.com" %datetime.now().microsecond
            email_address = "heattest@rs.com"
            domain_record_type = "A"

            parameters = {}
            if 'ssh_keypair_name' in yaml_template['parameters']:
                    keypair_name = rand_name("heat")
                    parameters['ssh_keypair_name'] = keypair_name
            if 'ssh_sync_keypair_name' in yaml_template['parameters']:
                    keypair_name = rand_name("heat")
                    parameters['ssh_sync_keypair_name'] = keypair_name
            if 'key_name' in yaml_template['parameters']:
                    parameters['key_name'] = 'sabeen'
            if 'key_name' in yaml_template['parameters'] and re.match('chef*', template):
                   keypair_name = rand_name("heat")
                   parameters['key_name'] = keypair_name
            if 'email_address' in yaml_template['parameters']:
                    parameters['email_address'] = email_address
            if 'domain_record_type' in yaml_template['parameters']:
                    parameters['domain_record_type'] = domain_record_type
            if 'domain_name' in yaml_template['parameters']:
                    parameters['domain_name'] = domain_name
            if 'service_domain' in yaml_template['parameters']:
                    parameters['service_domain'] = domain_name
            if 'git_url' in yaml_template['parameters']:
                parameters['git_url'] = "https://github.com/timductive/phphelloworld"
            if 'image_id' in yaml_template['parameters'] and image=="ubuntu":
                parameters['image_id'] = "80fbcb55-b206-41f9-9bc2-2dd7aac6c061"
            if 'image_id' in yaml_template['parameters'] and image=="centos":
                parameters['image_id'] = "ea8fdf8a-c0e4-4a1f-b17f-f5a421cda051"
            if 'flavor' in yaml_template['parameters']:
                parameters['flavor'] = "4GB Standard Instance"

            print "\nDeploying %s in %s using account %s" % (template, region, account)
            csresp, csbody, stack_identifier = self.create_stack(stack_name, region, yaml_template, parameters)

            if stack_identifier == 0:
                print "Stack create failed. Here's why: %s, %s" % (csresp, csbody)
                self.fail("Stack build failed.")
            else:
                stack_id = stack_identifier.split('/')[1]
                count = 0
                resp, body = self.get_stack(stack_id, region)
                if resp['status'] != '200':
                        print "The response is: %s" % resp
                        self.fail(resp)
                print "Stack %s status is: %s, %s" % (stack_name, body['stack_status'], body['stack_status_reason'])

                while body['stack_status'] == 'CREATE_IN_PROGRESS' and count < 90:
                    resp, body = self.get_stack(stack_id, region)
                    if resp['status'] == '200':
                        print "Deployment in %s status. Checking again in 1 minute" % body['stack_status']
                        time.sleep(60)
                        count += 1
                    elif resp['status'] != '200':
                        print "The response is: %s" % resp
                        pf += 1
                    elif body['stack_status'] == 'CREATE_FAILED':
                        print "Stack create failed. Here's why: %s" % body['stack_status_reason']
                        self._send_deploy_time_graphite(env, region, template, count, "failtime")
                        if os.environ.get('TEMPEST_CONFIG') == "tempest_qa.conf":
                            print "Deleting the stack now"
                            dresp, dbody = self.delete_stack(stack_name, stack_id, region)
                            if dresp['status'] != '204':
                                print "Delete did not work"
                        pf += 1
                    elif count == 90:
                        print "Stack create has taken over 90 minutes. Force failing now."
                        self._send_deploy_time_graphite(env, region, template, count, "failtime")
                        if os.environ.get('TEMPEST_CONFIG') == "tempest_qa.conf":
                            print "Stack create took too long. Deleting stack now."
                            dresp, dbody = self.delete_stack(stack_name, stack_id, region)
                            if dresp['status'] != '204':
                                print "Delete did not work"
                        pf += 1
                    else:
                        print "Something went wrong. Here's what: %s, %s" % (resp, body)
                        pf += 1

                if body['stack_status'] == 'CREATE_COMPLETE':
                    print "The deployment took %s minutes" % count
                    self._send_deploy_time_graphite(env, region, template, count, "buildtime")

                    resource_dict= self._get_resource_id(stack_id, stack_name,
                                                   region)
                    self._verify_resources(resource_dict)

                    #check DNS resource
                    if 'dns' in yaml_template['resources']:
                        domain_url = "domains"
                        self._verify_dns_entries(stack_name , stack_id,region,
                                                 email_address,
                            domain_record_type,domain_name)

                        result = self._verify_name_from_dns_api(domain_url,region,
                                  domain_name)
                        if result == True:
                            print "Domain name  %s exist ", domain_name
                        else:
                             print "Domain name  %s does not exist ",\
                                 domain_name

                    resp, body = self.get_stack(stack_id, region)

                    for output in body['outputs']:
                        if output['output_key'] == "server_ip":
                            url = "http://%s" % output['output_value']
                            customer_resp = requests.get(url, timeout=10)
                            print customer_resp
                            if customer_resp.status_code == '200':
                                print "http call to %s worked!" % url

                    #delete stack
                    print "Deleting stack now"
                    resp, body = self.delete_stack(stack_name, stack_id, region)
                    if resp['status'] != '204':
                        print "Delete did not work"
                    self._verify_resources(resource_dict)
                else:
                    print "Something went wrong! This could be the reason: %s" % body['stack_status_reason']

        #if more than 0 stacks fail, fail the test
        if pf > 0:
            self.fail("Stack build failed.")

    def _send_deploy_time_graphite(self, env, region, template, deploy_time, buildfail):
        cmd = 'echo "heat.' + env + '.build-tests.' + region + '.' + template \
              + '.' + buildfail + '  ' + str(deploy_time) \
              + ' `date +%s`" | ' \
                'nc graphite.staging.rs-heat.com ' \
                '2003 -q 2'
        os.system(cmd)
        print "Deploy time sent to graphite"

    def _verify_dns_entries(self,stack_name ,stack_id,region,email_address ,
                            domain_record_type,domain_name):
        print "Testing the DNS parameters "
        resp, body = self.orchestration_client.show_stack(stack_name,
                        stack_id ,region)
        if resp['status'] == 200:
            self.assertEquals(email_address, body['stack'][
                    'parameters']['email_address'])
            self.assertEquals(domain_record_type, body['stack']['parameters'][
                   'domain_record_type'])
            self.assertEquals(domain_name, body['stack'][
                   'parameters']['domain_name'])
            self.assertEquals("sabeen", body['stack']['parameters'][
                'key_name'])
        else:
         print "DNS verification fail for incorrect show-stack response"

    def _verify_name_from_dns_api(self,domain_url,region,
                                  domain_name):
        result = False
        dns_resp , dns_body = self.dns_client.list_domain_id(domain_url ,region )
        for domain in dns_body['domains']:
            if domain['name'] == domain_name:
                result = True

        return result

    def _verify_resources(self,resource_dict,region):

        resource_server = "OS::Nova::Server"
        resource_db = "OS::Trove::Instance"
        resource_lb = "Rackspace::Cloud::LoadBalancer"
        resource_cinder = "OS::Cinder::Volume"
        resource_keypair = "OS::Nova::KeyPair"
        resource_network = "Rackspace::Cloud::Network"
        resource_randomstr = "OS::Heat::RandomString"
        resource_grp = 'OS::Heat::ResourceGroup'
        resource_vol_attach = "OS::Cinder::VolumeAttachment"

        for key, value in resource_dict.iteritems():
            resource = key
            if resource == resource_server:
                server_id = value
                resp, body = self.servers_client.get_server(server_id,region)
                self._check_status_for_resource(resp['status'],resource_server)

            if resource == resource_lb:
                lb_id = value
                resp,body =self.loadbalancer_client.get_load_balancer(lb_id,
                                                                       region)
                self._check_status_for_resource(resp['status'],
                                                     resource_lb)
            if resource== resource_db:
                db_id = value
                resp, body = self.database_client.get_instance(db_id,
                                                                 region)
                self._check_status_for_resource(resp['status'],resource_db)

            if resource == resource_keypair:
                key_name = value
                resp, body = self.keypairs_client.get_keypair(key_name,
                                                                region)
                self._check_status_for_resource(resp['status'],resource_keypair)

            if resource == resource_cinder:
                    vol_id = value
                    resp,body =self.volume_client.get_volume(vol_id ,region)
                    self._check_status_for_resource(resp['status'],
                                                     resource_cinder)

            if resource == resource_vol_attach:
                    vol_id = value
                    resp,body =self.servers_client.get_volume_attachment(
                         server_id,vol_id,region)
                    self._check_status_for_resource(resp['status'],
                                                     resource_vol_attach)
            else:
                print "Resources does not exist in Stack "

        #         if resource['resource_type'] == resource_randomstr:
        #             random_str = resource['physical_resource_id']
        #             if random_str!=None:
        #                 print "%s is up." %resource_randomstr
        #             else:
        #                 print "%s is down" \
        #                      %resource_randomstr
        #
        #         if resource['resource_type'] == resource_grp:
        #             if resource['resource_status'] == "CREATE_COMPLETE":
        #                 print"%s is up." \
        #                        %resource_grp
        #             else :
        #                 print"%s is down." \
        #                       %resource_grp
        #
        #

    def _check_status_for_resource(self, status_code, resource):
        if status_code =='200':
            print "%s is up." %resource
        if status_code =='404':
            print "%s is down." %resource

    def _get_resource_id(self,stack_name,stack_id,region):
        resource_ids={}

        resource_server = "OS::Nova::Server"
        resource_db = "OS::Trove::Instance"
        resource_lb = "Rackspace::Cloud::LoadBalancer"
        resource_cinder = "OS::Cinder::Volume"
        resource_keypair = "OS::Nova::KeyPair"
        resource_network = "Rackspace::Cloud::Network"
        resource_randomstr = "OS::Heat::RandomString"
        resource_grp = 'OS::Heat::ResourceGroup'
        resource_vol_attach = "OS::Cinder::VolumeAttachment"
        resp, body = self.orchestration_client.list_resources(stack_name,stack_id, region)
        if resp['status'] == '200':
            for resource in body:
                if resource['resource_type'] == resource_server:
                    resource_ids.update({resource['resource_type']:resource['physical_resource_id']})
                if resource['resource_type'] == resource_db:
                    resource_ids.update({resource['resource_type']:resource['physical_resource_id']})
                if resource['resource_type'] == resource_lb:
                    resource_ids.update({resource['resource_type']:resource['physical_resource_id']})
                if resource['resource_type'] ==resource_network:
                    resource_ids.update({resource['resource_type']:resource['physical_resource_id']})
                if resource['resource_type'] == resource_keypair:
                    resource_ids.update({resource['resource_type']:resource['physical_resource_id']})
                if resource['resource_type'] == resource_cinder:
                    resource_ids.update({resource['resource_type']:resource['physical_resource_id']})
                if resource['resource_type'] == resource_vol_attach:
                    resource_ids.update({resource['resource_type']:resource['physical_resource_id']})
        return resource_ids