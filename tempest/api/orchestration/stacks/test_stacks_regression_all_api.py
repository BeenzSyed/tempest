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
import pdb


LOG = logging.getLogger(__name__)

adopt_data = """
"status": "COMPLETE",
    "name": "devstack",
    "template": {
        "outputs": {
            "public_ip": {
                "description": "The public ip address of the server",
                "value": {
                    "get_attr": [
                        "devstack_server",
                        "accessIPv4"
                    ]
                }
            },
            "private_ip": {
                "description": "The private ip address of the server",
                "value": {
                    "get_attr": [
                        "devstack_server",
                        "privateIPv4"
                    ]
                }
            }
        },
        "heat_template_version": "2013-05-23",
        "description": "A template implementation of a resource that provides a Devstack server\n",
        "parameters": {
            "mysql_pass": {
                "default": "admin",
                "hidden": true,
                "type": "string",
                "description": "The database admin account password",
                "constraints": [
                    {
                        "length": {
                            "max": 41,
                            "min": 1
                        },
                        "description": "must be between 1 and 41 characters"
                    },
                    {
                        "allowed_pattern": "[a-zA-Z0-9]*",
                        "description": "must contain only alphanumeric characters."
                    }
                ]
            },
            "admin_pass": {
                "default": "admin",
                "hidden": true,
                "type": "string",
                "description": "The database admin account password",
                "constraints": [
                    {
                        "length": {
                            "max": 41,
                            "min": 1
                        },
                        "description": "must be between 1 and 41 characters"
                    },
                    {
                        "allowed_pattern": "[a-zA-Z0-9]*",
                        "description": "must contain only alphanumeric characters."
                    }
                ]
            },
            "service_pass": {
                "default": "admin",
                "hidden": true,
                "type": "string",
                "description": "The service password which is used by the OpenStack services to authenticate with Keystone.",
                "constraints": [
                    {
                        "length": {
                            "max": 41,
                            "min": 1
                        },
                        "description": "must be between 1 and 41 characters"
                    },
                    {
                        "allowed_pattern": "[a-zA-Z0-9]*",
                        "description": "must contain only alphanumeric characters."
                    }
                ]
            },
            "server_name": {
                "default": "Devstack server",
                "type": "string",
                "description": "the instance name"
            },
            "key_name": {
                "required": true,
                "type": "string",
                "description": "Nova keypair name for ssh access to the server"
            },
            "image": {
                "default": "Ubuntu 12.04 LTS (Precise Pangolin)",
                "type": "string",
                "description": "Server image id to use",
                "constraints": [
                    {
                        "description": "must be a Devstack-supported distro",
                        "allowed_values": [
                            "CentOS 6.4",
                            "Red Hat Enterprise Linux 6.4",
                            "Ubuntu 12.04 LTS (Precise Pangolin)",
                            "Fedora 18 (Spherical Cow)"
                        ]
                    }
                ]
            },
            "rabbit_pass": {
                "default": "admin",
                "hidden": true,
                "type": "string",
                "description": "The RabbitMQ service admin password",
                "constraints": [
                    {
                        "length": {
                            "max": 41,
                            "min": 1
                        },
                        "description": "must be between 1 and 41 characters"
                    },
                    {
                        "allowed_pattern": "[a-zA-Z0-9]*",
                        "description": "must contain only alphanumeric characters."
                    }
                ]
            },
            "enable_heat": {
                "default": "false",
                "type": "string",
                "description": "Enable the Heat service in Devstack",
                "constraints": [
                    {
                        "description": "must be either \"true\" or \"false\"",
                        "allowed_values": [
                            "true",
                            "false"
                        ]
                    }
                ]
            },
            "devstack_branch": {
                "default": "master",
                "type": "string",
                "description": "Devstack branch to clone"
            },
            "flavor": {
                "default": "2GB Standard Instance",
                "type": "string",
                "description": "Rackspace Cloud Server flavor",
                "constraints": [
                    {
                        "description": "must be a valid Rackspace Cloud Server flavor large enough to run devstack",
                        "allowed_values": [
                            "1GB Standard Instance",
                            "2GB Standard Instance",
                            "4GB Standard Instance",
                            "8GB Standard Instance",
                            "15GB Standard Instance",
                            "30GB Standard Instance"
                        ]
                    }
                ]
            }
        },
        "resources": {
            "devstack_server": {
                "type": "Rackspace::Cloud::Server",
                "properties": {
                    "key_name": {
                        "get_param": "key_name"
                    },
                    "flavor": {
                        "get_param": "flavor"
                    },
                    "user_data": {
                        "str_replace": {
                            "params": {
                                "%service_pass%": {
                                    "get_param": "service_pass"
                                },
                                "%enable_heat%": {
                                    "get_param": "enable_heat"
                                },
                                "%key_name%": {
                                    "get_param": "key_name"
                                },
                                "%image%": {
                                    "get_param": "image"
                                },
                                "%mysql_pass%": {
                                    "get_param": "mysql_pass"
                                },
                                "%admin_pass%": {
                                    "get_param": "admin_pass"
                                },
                                "%rabbit_pass%": {
                                    "get_param": "rabbit_pass"
                                },
                                "%devstack_branch%": {
                                    "get_param": "devstack_branch"
                                }
                            },
                            "template": "#!/bin/bash -x\n\n# Install requirements\npackages=\"git emacs nmap\"\nif [[ \"%image%\" == \"Ubuntu 12.04 LTS (Precise Pangolin)\" ]]; then\n    apt-get install -y $packages\nelse\n    yum -y install $packages\nfi\n\n# Configure and install Devstack\ngroupadd stack\nuseradd -g stack -s /bin/bash -d /opt/stack -m stack\necho \"stack ALL=(ALL) NOPASSWD: ALL\" >> /etc/sudoers\n\ncat >~stack/install-devstack.sh<<EOF\n#!/bin/bash -x\n\ncd ~stack\ngit clone git://github.com/openstack-dev/devstack.git -b \"%devstack_branch%\"\ncd devstack\nif [[ \"%enable_heat%\" == \"true\" ]]; then\n    echo \"enable_service heat h-api h-api-cfn h-api-cw h-eng\" > localrc\nfi\nif [[ -n \"%admin_pass%\" ]]; then\n    echo \"ADMIN_PASSWORD=%admin_pass%\" >> localrc\nfi\nif [[ -n \"%mysql_pass%\" ]]; then\n    echo \"MYSQL_PASSWORD=%mysql_pass%\" >> localrc\nfi\nif [[ -n \"%rabbit_pass%\" ]]; then\n    echo \"RABBIT_PASSWORD=%rabbit_pass%\" >> localrc\nfi\nif [[ -n \"%service_pass%\" ]]; then\n    echo \"SERVICE_PASSWORD=%service_pass%\" >> localrc\nfi\necho \"SERVICE_TOKEN=$(openssl rand -hex 10)\" >> localrc\n\nsudo -u stack ~stack/devstack/stack.sh\n\n# Add the SSH key to the stack user\nmkdir ~stack/.ssh && chmod 700 ~stack/.ssh\nsudo tail -n1 /root/.ssh/authorized_keys > ~stack/.ssh/authorized_keys\nchmod 400 ~stack/.ssh/authorized_keys\n\n# Add the key to nova\nnova --os-username admin --os-password \"%admin_pass%\" --os-tenant-name admin --os-auth-url http://localhost:5000/v2.0/ keypair-add \"%key_name%\" --pub-key ~stack/.ssh/authorized_keys\n\n# Heat-specific configs below\n[[ \"%enable_heat%\" != \"true\" ]] && exit 0\n\n# Download convenience functions for Heat\ncurl https://raw.github.com/jasondunsmore/heat-shell/master/functions > ~/.bash_profile\nsource ~stack/.bash_profile\n\n# Download & install prebuilt Heat JEOS images\nglance_create F17-i386-cfntools http://fedorapeople.org/groups/heat/prebuilt-jeos-images/F17-i386-cfntools.qcow2\nglance_create F17-x86_64-cfntools http://fedorapeople.org/groups/heat/prebuilt-jeos-images/F17-x86_64-cfntools.qcow2\nglance_create F18-i386-cfntools http://fedorapeople.org/groups/heat/prebuilt-jeos-images/F18-i386-cfntools.qcow2\nglance_create F18-x86_64-cfntools http://fedorapeople.org/groups/heat/prebuilt-jeos-images/F18-x86_64-cfntools.qcow2\nEOF\nchmod +x ~stack/install-devstack.sh\nsudo -u stack ~stack/install-devstack.sh\n"
                        }
                    },
                    "image": {
                        "get_param": "image"
                    },
                    "name": {
                        "get_param": "server_name"
                    }
                }
            }
        }
}"""

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
        #env = "dev"
        template_giturl = "https://raw2.github.com/heat-ci/heat-templates/master/" + env + "/" + template + ".template"
        #print template_giturl
        response_templates = requests.get(template_giturl, timeout=3)
        yaml_template = yaml.safe_load(response_templates.content)
        #print yaml_template

        parameters = {}
        if 'key_name' in yaml_template['parameters']:
            parameters = {
                'key_name': 'sabeen'
            }
        if 'git_url' in yaml_template['parameters']:
            parameters['git_url'] = "https://github.com/timductive/phphelloworld"
            #https://github.com/beenzsyed/phphelloworld

        #region = "Dev"
        rstype = "Rackspace::Cloud::Server"
        rsname = "devstack_server"

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
            create_stack_name = "CREATE_%s" %datetime.datetime.now().microsecond
            csresp, csbody, stack_identifier = self.create_stack(create_stack_name, region, yaml_template, parameters)
            self._check_resp(csresp, csbody, apiname)

            #update stack
            apiname = "update stack"
            parameters = {
                    'key_name': 'sabeen',
                    'flavor': '1GB Standard Instance'
            }
            #pdb.set_trace()
            updateStackName, updateStackId = self._get_stacks("UPDATE_", stacklist)
            if updateStackName != 0:
                ssresp, ssbody = self.update_stack(updateStackId, updateStackName, region, yaml_template, parameters)
                self._check_resp(ssresp, ssbody, apiname)

            #stack show
            apiname = "show stack"
            if updateStackName != 0:
                ssresp, ssbody = self.orchestration_client.show_stack(updateStackName, updateStackId, region)
                self._check_resp(ssresp, ssbody, apiname)

            #delete stack
            apiname = "delete stack"
            deleteStackName, deleteStackId = self._get_stacks("CREATE_", stacklist)
            if deleteStackName != 0:
                ssresp, ssbody = self.orchestration_client.delete_stack(deleteStackName, deleteStackId, region)
                self._check_resp(ssresp, ssbody, apiname)

            #abandon stack
            apiname = "abandon stack"
            abandonStackName, abandonStackId = self._get_stacks("ADOPT_", stacklist)
            if abandonStackName != 0:
                asresp, asbody, = self.abandon_stack(abandonStackId, abandonStackName, region)
                self._check_resp(asresp, asbody, apiname)

            apiname = "adopt stack"
            adopt_stack_name = "ADOPT_%s" %datetime.datetime.now().microsecond
            #pdb.set_trace()
            asresp, asbody, stack_identifier = self.adopt_stack(adopt_stack_name, region, adopt_data, yaml_template, parameters)
            self._check_resp(asresp, asbody, apiname)

            #-------  Stack events  ----------
            #event list
            apiname = "list event"
            if updateStackName != 0:
                evresp, evbody = self.orchestration_client.list_events(updateStackName, updateStackId, region)
                self._check_resp(evresp, evbody, apiname)

            #event show
            apiname = "show event"
            if updateStackName != 0:
                event_id = self._get_event_id(evbody)
                esresp, esbody = self.orchestration_client.show_event(updateStackName, updateStackId, rsname, event_id, region)
                self._check_resp(esresp, esbody, apiname)


            #-------  Templates  -------------
            #template show
            apiname = "template show"
            if updateStackName != 0:
                tsresp, tsbody = self.orchestration_client.show_template(updateStackName, updateStackId, region)
                self._check_resp(tsresp, tsbody, apiname)

            #template validate
            apiname = "template validate"
            tvresp, tvbody = self.orchestration_client.validate_template(region, yaml_template, parameters)
            self._check_resp(tvresp, tvbody, apiname)


            #--------  Stack resources  --------
            #Lists resources in a stack
            apiname = "list resources"
            if updateStackName != 0:
                lrresp, lrbody = self.orchestration_client.list_resources(updateStackName, updateStackId, region)
                self._check_resp(lrresp, lrbody, apiname)

            #Gets metadata for a specified resource.
            apiname = "resource metadata"
            if updateStackName != 0:
                rmresp, rmbody = self.orchestration_client.show_resource_metadata(updateStackName, updateStackId, rsname, region)
                self._check_resp(rmresp, rmbody, apiname)

            #Gets data for a specified resource.
            apiname = "get resources"
            if updateStackName != 0:
                rsresp, rsbody = self.orchestration_client.get_resource(updateStackName, updateStackId, rsname, region)
                self._check_resp(rsresp, rsbody, apiname)

            #Gets a template representation for a specified resource type.
            apiname = "resource template"
            rtresp, rtbody = self.orchestration_client.resource_template(rstype, region)
            self._check_resp(rtresp, rtbody, apiname)

            #Lists the supported template resource types.
            apiname = "template resource types"
            rtresp, rtbody = self.orchestration_client.template_resource(region)
            self._check_resp(rtresp, rtbody, apiname)

            #Gets the interface schema for a specified resource type.
            apiname = "schema for resource type"
            rtresp, rtbody = self.orchestration_client.resource_schema(rstype, region)
            self._check_resp(rtresp, rtbody, apiname)

        if updateStackName == 0:
            print "Create a stack named UPDATE_123 so that I can verify more api calls"

        if self.fail_flag == 0:
            print "All api's are up!"
        elif self.fail_flag > 0:
            print "One or more api's failed. Look above."
            self.fail("One or more api's failed.")

        # #suspend stack, wait 1 min
        # print "suspend stack"
        # ssresp, ssbody = self.orchestration_client.suspend_stack(stack_name, region)
        # self._check_resp(ssresp, ssbody, "suspend stack")
        #
        # time.sleep(60)
        #
        # #resume stack
        # print "resume stack"
        # rsresp, rsbody = self.client.resume_stack(stack_id, region)
        # self._check_resp(rsresp, rsbody, "resume stack")


    def _send_deploy_time_graphite(self, env, region, template, deploy_time, buildfail):
        cmd = 'echo "heat.' + env + '.build-tests.' + region + '.' + template \
              + '.' + buildfail + '  ' + str(deploy_time) \
              + ' `date +%s`" | ' \
                'nc graphite.staging.rs-heat.com ' \
                '2003 -q 2'
        #print cmd
        os.system(cmd)
        print "Deploy time sent to graphite"

    def _check_resp(self, resp, body, apiname):
        if resp['status'] == '200' or resp['status'] == '201' or resp['status'] == '202' or resp['status'] == '204':
            print "%s worked! The response is: %s" % (apiname, resp['status'])
        else:
            print "%s did not work. The response is: %s %s" % (apiname, resp['status'], body)
            self.fail_flag += 1

    def _get_stacks(self, typestack, body):
        for stackname in body:
            match = re.search(typestack + '_*', stackname['stack_name'])
            if match:
                return stackname['stack_name'], stackname['id']
        return 0, 0

    def _get_event_id(self, body):
        for stackname in body:
            return stackname['id']




