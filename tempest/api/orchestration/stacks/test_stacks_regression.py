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

LOG = logging.getLogger(__name__)


class StacksTestJSON(base.BaseOrchestrationTest):
    _interface = 'json'

    @classmethod
    def setUpClass(cls):
        super(StacksTestJSON, cls).setUpClass()
        cls.client = cls.orchestration_client

    def test_wordpress_multi_realDeployment(self):
        self._test_stack("wordpress-multi")

    def test_all(self):
        self._test_stack()

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

            respbi, bodybi = self.orchestration_client.get_build_info(region)
            print "\nThe build info is: %s\n" % bodybi

            #Check whether the parameter has a label (display in Reach)
            all_parameters = yaml_template['parameters']
            for param in all_parameters:
                if 'label' not in yaml_template['parameters'][param]:
                    print "label does not exist for %s" % param

            stack_name = rand_name("qe_"+template+region)
            domain = rand_name("iloveheat")
            params = self._set_parameters(yaml_template, template, region, image, domain)

            print "\nDeploying %s in %s using account %s" % (template, region, account)
            csresp, csbody, stack_identifier = self.create_stack(stack_name, region, yaml_template, params)

            if stack_identifier == 0:
                print "Stack create failed. Here's why: %s, %s" % (csresp, csbody)
                self.fail("Stack build failed.")
            else:
                stack_id = stack_identifier.split('/')[1]
                count = 0
                retry = 0

                #pdb.set_trace()
                should_restart = True
                while should_restart:
                    resp, body = self.get_stack(stack_id, region)
                    if retry == 4:
                        print "Retried 4 times! Stack create failed."
                        self._send_deploy_time_graphite(env, region, template, count, "failtime")
                        pf += 1
                        should_restart = False
                    elif resp['status'] != '200':
                        print "The response is: %s" % resp
                        #Retry
                        stack_name = rand_name("qe_"+template+region)
                        domain = rand_name("iloveheat")
                        params = self._set_parameters(yaml_template, template, region, image, domain)
                        csresp, csbody, stack_identifier = self.create_stack(stack_name, region, yaml_template, params)
                        if stack_identifier == 0:
                            print "Stack create failed. Here's why: %s, %s" % (csresp, csbody)
                            self.fail("Stack build failed.")
                        else:
                            stack_id = stack_identifier.split('/')[1]
                            retry += 1
                    else:
                        if body['stack_status'] == 'CREATE_IN_PROGRESS' and count < 90:
                            print "Deployment in %s status. Checking again in 1 minute" % body['stack_status']
                            time.sleep(60)
                            count += 1
                        elif body['stack_status'] == 'CREATE_IN_PROGRESS' and count == 90:
                            print "Stack create has taken over 90 minutes. Force failing now."
                            self._send_deploy_time_graphite(env, region, template, count, "failtime")
                            pf += 1
                            should_restart = False

                        elif body['stack_status'] == 'CREATE_FAILED' and retry < 4:
                            print "Stack create failed. Here's why: %s" % body['stack_status_reason']
                            ssresp, ssbody = self.orchestration_client.show_stack(stack_name, stack_id, region)
                            print "Stack show output: %s" % ssbody
                            #Retry
                            stack_name = rand_name("qe_"+template+region)
                            domain = rand_name("iloveheat")
                            params = self._set_parameters(yaml_template, template, region, image, domain)
                            csresp, csbody, stack_identifier = self.create_stack(stack_name, region, yaml_template, params)
                            if stack_identifier == 0:
                                print "Stack create failed. Here's why: %s, %s" % (csresp, csbody)
                                self.fail("Stack build failed.")
                            else:
                                #Trying the retries
                                stack_id = stack_identifier.split('/')[1]
                                retry += 1

                        elif body['stack_status'] == 'CREATE_COMPLETE':
                            print "The deployment took %s minutes" % count
                            self._send_deploy_time_graphite(env, region, template, count, "buildtime")

                            resource_dict = self._get_resource_id(stack_name, stack_id, region)
                            self._verify_resources(resource_dict, region, domain)

                            #for wordpress an http call is made to ensure it is up
                            resp, body = self.get_stack(stack_id, region)
                            #print body['outputs']
                            for output in body['outputs']:
                                if output['output_key'] == "server_ip":
                                    #http call
                                    url = "http://%s" % output['output_value']
                                    print "The url is %s" % url
                                    try:
                                        customer_resp = requests.get(url, timeout=10, verify=False)
                                        #print customer_resp.status_code
                                        if customer_resp.status_code == 200:
                                            print "http call to %s worked!" % url
                                    except Exception as e:
                                        print "http call did not work!"

                                    #ssh call
                                    # client = paramiko.SSHClient()
                                    # client.load_system_host_keys()
                                    # client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                                    # try:
                                    #     ip = output['output_value']
                                    #     #passwd = resources[int_key]['instance']['password']
                                    #     client.connect(ip, timeout=10, port=22, username="root",
                                    #                    password=passwd)
                                    #     # print "Checking %s with password %s: %s" % (ip, passwd,
                                    #     #                                         validate_passed)
                                    # except Exception as e:
                                    #     print "ssh did not work!"
                                    #     client.close()

                            #update stack
                            print "Updating Stack"
                            resp_update, body_update = self.orchestration_client.update_stack(
                                             stack_identifier = stack_id,
                                             name = stack_name,
                                             region = region,
                                             parameters=params,
                                             template=yaml_template)
                            if resp_update['status'] =='202':
                                print "Update request went successfully"
                            else:
                                print resp_update['status']
                                print "Something went wrong during update"

                            #delete stack
                            print "Deleting stack now"
                            self._delete_stack(stack_name, stack_id, region)
                            should_restart = False

                        else:
                            print "Stack in %s state" % body['stack_status']
                            print "Something went wrong. Stack failed!"
                            pf += 1
                            should_restart = False

        #if more than 0 stacks fail, fail the test
        if pf > 0:
            self.fail("Stack build failed.")

    def _set_parameters(self, yaml_template, template, region, image, domain):
        domain_name = "example%s.com" %datetime.now().microsecond
        email_address = "heattest@rs.com"
        domain_record_type = "A"

        parameters = {}
        if 'ssh_keypair_name' in yaml_template['parameters']:
            keypair_name = rand_name("heat")
            parameters['ssh_keypair_name'] = keypair_name
        if 'ssh_keypair_name' in yaml_template['parameters'] and re.match('ansible*', template):
            parameters['ssh_keypair_name'] = 'sabeen'
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
        if 'domain_name' in yaml_template['parameters']:
            parameters['domain_name'] = domain_name
        if (region == 'HKG' or region == 'SYD') and 'devops_flavor' in yaml_template['parameters']:
            parameters['devops_flavor'] = "4GB Standard Instance"
        if (region == 'HKG' or region == 'SYD') and 'api_flavor_ref' in yaml_template['parameters']:
            parameters['api_flavor_ref'] = "3"
        if 'db_pass' in yaml_template['parameters']:
            parameters['db_pass'] = "secretes"
        if 'database_server_flavor' in yaml_template['parameters']:
            parameters['database_server_flavor'] = "4GB Standard Instance"
        if 'wp_master_server_flavor' in yaml_template['parameters']:
            parameters['wp_master_server_flavor'] = "4GB Standard Instance"
        if 'wp_web_server_flavor' in yaml_template['parameters']:
            parameters['wp_web_server_flavor'] = "4GB Standard Instance"
        if 'server_flavor' in yaml_template['parameters']:
            parameters['server_flavor'] = "4GB Standard Instance"

        print "\nParameters are set to %s" % parameters
        return parameters

    def _send_deploy_time_graphite(self, env, region, template, deploy_time, buildfail):
        cmd = 'echo "heat.' + env + '.build-tests.' + region + '.' + template \
              + '.' + buildfail + '  ' + str(deploy_time) \
              + ' `date +%s`" | ' \
                'nc graphite.staging.rs-heat.com ' \
                '2003 -q 2'
        os.system(cmd)
        print "Deploy time sent to graphite"

    def _delete_stack(self, stack_name, stack_id, region):
        print "Deleting stack now"
        resp, body = self.delete_stack(stack_name, stack_id, region)
        if resp['status'] != '204':
            print "Delete did not work"

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

    def _verify_name_from_dns_api(self, domain_url, region,
                                  domain_name):
        result = False
        dns_resp , dns_body = self.dns_client.list_domain_id(domain_url, region)
        for domain in dns_body['domains']:
            if domain['name'] == domain_name:
                result = True

        return result

    def _verify_resources(self, resource_dict, region, domain):

        resource_server = "OS::Nova::Server"
        resource_db = "OS::Trove::Instance"
        resource_lb = "Rackspace::Cloud::LoadBalancer"
        resource_cinder = "OS::Cinder::Volume"
        resource_keypair = "OS::Nova::KeyPair"
        resource_network = "Rackspace::Cloud::Network"
        resource_randomstr = "OS::Heat::RandomString"
        resource_grp = 'OS::Heat::ResourceGroup'
        resource_vol_attach = "OS::Cinder::VolumeAttachment"
        resource_dns = "Rackspace::Cloud::DNS"
        resource_randomstr = "OS::Heat::RandomString"
        resource_grp = 'OS::Heat::ResourceGroup'

        if region == 'QA' or region == 'Dev' or region == 'Staging':
            region = 'dfw'

        #print resource_dict
        for key, value in resource_dict.iteritems():
            resource = key
            if resource == resource_server:
                server_id = value
                resp, body = self.servers_client.get_server(server_id,region)
                self._check_status_for_resource(resp['status'], resource_server)

            elif resource == resource_network:
                network_id = value
                #pdb.set_trace()
                resp, body = self.network_client.list_network(self.config.identity['tenant_name'], network_id, region)
                self._check_status_for_resource(resp['status'], resource_server)

            elif resource == resource_lb:
                lb_id = value
                resp, body =self.loadbalancer_client.get_load_balancer(lb_id,
                                                                       region)
                self._check_status_for_resource(resp['status'],
                                                     resource_lb)
            elif resource == resource_db:
                db_id = value
                resp, body = self.database_client.get_instance(db_id,
                                                                 region)
                self._check_status_for_resource(resp['status'],resource_db)

            elif resource == resource_keypair:
                key_name = value
                resp, body = self.keypairs_client.get_keypair(key_name,
                                                                region)
                self._check_status_for_resource(resp['status'], resource_keypair)

            elif resource == resource_cinder:
                vol_id = value
                resp, body =self.volume_client.get_volume(vol_id, region)
                self._check_status_for_resource(resp['status'],
                                                 resource_cinder)

            elif resource == resource_vol_attach:
                vol_id = value
                resp,body =self.servers_client.get_volume_attachment(
                     server_id, vol_id, region)
                self._check_status_for_resource(resp['status'],
                                                 resource_vol_attach)

            elif resource == resource_dns:
                #pdb.set_trace()
                dns_val = value
                resp, body = self.dns_client.list_domain_id(dns_val, region)
                #print "body name %s" % body['name']
                #print "domain name %s" % domain
                if body['name'].split('.')[0] == domain:
                        print "%s is up." % resource_dns
                else:
                        print "%s is down." % resource_dns

            elif resource == resource_randomstr:
                    random_str = value
                    if random_str!=None:
                        print "%s is up." % resource_randomstr
                    else:
                        print "%s is down" % resource_randomstr

            elif resource == resource_grp:
                    res_grp = value
                    if res_grp!=None:
                       print"%s is up." % resource_grp
                    else :
                        print"%s is down." % resource_grp

            else:
                print "This resource: %s does not exist in the stack" % resource

    def _check_status_for_resource(self, status_code, resource):
        if status_code =='200':
            print "%s is up." %resource
        if status_code =='404':
            print "%s is down." %resource

    def _get_resource_id(self, stack_name, stack_id, region):

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
        resource_dns = "Rackspace::Cloud::DNS"
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
                if resource['resource_type'] == resource_dns:
                    resource_ids.update({resource['resource_type']:resource['physical_resource_id']})
                if resource['resource_type'] == resource_randomstr:
                    resource_ids.update({resource['resource_type']:resource['physical_resource_id']})
                if resource['resource_type'] == resource_grp:
                    resource_ids.update({resource['resource_type']:resource['physical_resource_id']})
        return resource_ids
