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
import urllib2
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
        usertype = self.config.identity['username']
        print "User is: %s" % usertype
        print "Environment is %s" % env

        req = urllib2.urlopen("https://github.rackspace.com/Heat/cookbook-heat/raw/master/files/default/policy.json")
        policy_details = yaml.load(req)
        print policy_details

        #print "request is: %s" % req
        #html = req.read()
        #print "html is %s" % html
        #print type(html)
        #policy_details = yaml.load(html.content)

        # policy_file = "https://github.rackspace.com/Heat/cookbook-heat/raw/master/files/default/policy.json"
        # policy = requests.get(policy_file, timeout=10)
        # if policy.status_code != requests.codes.ok:
        #     print "This file does not exist: %s" % policy_file
        #     self.fail("The policy file does not exist.")
        # else:
        #     policy_details = yaml.safe_load(policy.content)

        super_user = policy_details['allow_management_api_user'].split(":")[2]
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
            elif slrespm['status'] == '403':
                print "%s does not have access. Error: %s" % (usertype, stacklistm)
        else:
            if slrespm['status'] == '403':
                print "%s is not a superuser and does not have access." % (usertype)
            else:
                print "%s is not a superuser and has access." % (usertype)
                self.fail("Something is wrong! A normal user has superuser access.")

            # if (numstacksmgmt == numstacks):
            #     print "The user %s is not a super user. Stack list gives back %s stacks and the management api gives back %s stacks." %(usertype, numstacks, numstacksmgmt)
            # else:
            #     print "Something is wrong. The user %s is not a super user. Stack list gives back %s stacks and the management api gives back %s stacks." %(usertype, numstacks, numstacksmgmt)
            #     self.fail("Management api is not working.")

    def _get_stacks(self, typestack, body):
        for stackname in body:
            match = re.search(typestack + '_*', stackname['stack_name'])
            if match:
                return stackname['stack_name'], stackname['id']
        return 0, 0

    def _get_event_id(self, body):
        for stackname in body:
            return stackname['id']




