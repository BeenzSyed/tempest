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
from testconfig import config
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

adopt_data2 = """
{"status": "COMPLETE", "name": "ADOPT_554748", "stack_user_project_id": "883286", "environment": {"parameters": {"server_hostname": "WordPress", "username": "wp_user", "domain": "example1234.com", "image": "Ubuntu 12.04 LTS (Precise Pangolin)", "chef_version": "11.16.2", "prefix": "wp_", "version": "3.9.2", "flavor": "2 GB Performance", "database_name": "wordpress", "kitchen": "https://github.com/rackspace-orchestration-templates/wordpress-single.git"}, "resource_registry": {"resources": {}}}, "template": {"parameter_groups": [{"parameters": ["server_hostname", "image", "flavor"], "label": "Server Settings"}, {"parameters": ["domain", "username"], "label": "WordPress Settings"}, {"parameters": ["kitchen", "chef_version", "version", "prefix"], "label": "rax-dev-params"}], "heat_template_version": "2013-05-23", "description": "This is a Heat template to deploy a single Linux server running WordPress.\\n", "parameters": {"server_hostname": {"default": "WordPress", "label": "Server Name", "type": "string", "description": "Hostname to use for the server that\'s built.", "constraints": [{"length": {"max": 64, "min": 1}}, {"allowed_pattern": "^[a-zA-Z][a-zA-Z0-9-]*$", "description": "Must begin with a letter and contain only alphanumeric characters.\\n"}]}, "username": {"default": "wp_user", "label": "Username", "type": "string", "description": "Username for system, database, and WordPress logins.", "constraints": [{"allowed_pattern": "^[a-zA-Z0-9 _.@-]{1,16}$", "description": "Must be shorter than 16 characters and may only contain alphanumeric\\ncharacters, \' \', \'_\', \'.\', \'@\', and/or \'-\'.\\n"}]}, "domain": {"default": "example.com", "label": "Site Domain", "type": "string", "description": "Domain to be used with WordPress site", "constraints": [{"allowed_pattern": "^[a-zA-Z0-9.-]{1,255}.[a-zA-Z]{2,15}$", "description": "Must be a valid domain name"}]}, "database_name": {"default": "wordpress", "label": "Database Name", "type": "string", "description": "WordPress database name", "constraints": [{"allowed_pattern": "^[0-9a-zA-Z$_]{1,64}$", "description": "Maximum length of 64 characters, may only contain letters, numbers, and\\nunderscores.\\n"}]}, "chef_version": {"default": "11.16.2", "type": "string", "description": "Version of chef client to use", "label": "Chef Version"}, "prefix": {"default": "wp_", "label": "Database Prefix", "type": "string", "description": "Prefix to use for WordPress database tables", "constraints": [{"allowed_pattern": "^[0-9a-zA-Z$_]{0,10}$", "description": "Prefix must be shorter than 10 characters, and can only include\\nletters, numbers, $, and/or underscores.\\n"}]}, "version": {"default": "3.9.2", "label": "WordPress Version", "type": "string", "description": "Version of WordPress to install", "constraints": [{"allowed_values": ["3.9.2"]}]}, "flavor": {"default": "1 GB Performance", "label": "Server Size", "type": "string", "description": "Required: Rackspace Cloud Server flavor to use. The size is based on the\\namount of RAM for the provisioned server.\\n", "constraints": [{"description": "Must be a valid Rackspace Cloud Server flavor for the region you have\\nselected to deploy into.\\n", "allowed_values": ["1 GB Performance", "2 GB Performance", "4 GB Performance", "8 GB Performance", "15 GB Performance", "30 GB Performance", "1GB Standard Instance", "2GB Standard Instance", "4GB Standard Instance", "8GB Standard Instance", "15GB Standard Instance", "30GB Standard Instance"]}]}, "image": {"default": "Ubuntu 12.04 LTS (Precise Pangolin)", "label": "Operating System", "type": "string", "description": "Required: Server image used for all servers that are created as a part of\\nthis deployment.\\n", "constraints": [{"description": "Must be a supported operating system.", "allowed_values": ["Ubuntu 12.04 LTS (Precise Pangolin)"]}]}, "kitchen": {"default": "https://github.com/rackspace-orchestration-templates/wordpress-single.git", "type": "string", "description": "URL for a git repo containing required cookbooks", "label": "Kitchen URL"}}, "outputs": {"mysql_root_password": {"description": "MySQL Root Password", "value": {"get_attr": ["mysql_root_password", "value"]}}, "wordpress_password": {"description": "WordPress Password", "value": {"get_attr": ["database_password", "value"]}}, "private_key": {"description": "SSH Private Key", "value": {"get_attr": ["ssh_key", "private_key"]}}, "server_ip": {"description": "Server IP", "value": {"get_attr": ["wordpress_server", "accessIPv4"]}}, "wordpress_user": {"description": "WordPress User", "value": {"get_param": "username"}}}, "resources": {"sync_key": {"type": "OS::Nova::KeyPair", "properties": {"name": {"str_replace": {"params": {"%stack_id%": {"get_param": "OS::stack_id"}}, "template": "%stack_id%-sync"}}, "save_private_key": true}}, "wp_secure_auth": {"type": "OS::Heat::RandomString", "properties": {"length": 32, "sequence": "hexdigits"}}, "wordpress_server": {"type": "Rackspace::Cloud::Server", "properties": {"key_name": {"get_resource": "ssh_key"}, "flavor": {"get_param": "flavor"}, "image": {"get_param": "image"}, "name": {"get_param": "server_hostname"}, "metadata": {"rax-heat": {"get_param": "OS::stack_id"}}}}, "mysql_root_password": {"type": "OS::Heat::RandomString", "properties": {"length": 16, "sequence": "lettersdigits"}}, "mysql_debian_password": {"type": "OS::Heat::RandomString", "properties": {"length": 16, "sequence": "lettersdigits"}}, "ssh_key": {"type": "OS::Nova::KeyPair", "properties": {"name": {"get_param": "OS::stack_id"}, "save_private_key": true}}, "wp_auth": {"type": "OS::Heat::RandomString", "properties": {"length": 32, "sequence": "hexdigits"}}, "wordpress_setup": {"depends_on": "wordpress_server", "type": "OS::Heat::ChefSolo", "properties": {"node": {"varnish": {"version": "3.0", "listen_port": "80"}, "sysctl": {"values": {"fs.inotify.max_user_watches": 1000000}}, "lsyncd": {"interval": 5}, "monit": {"mail_format": {"from": "monit@localhost"}, "notify_email": "root@localhost"}, "vsftpd": {"chroot_local_user": false, "ssl_ciphers": "AES256-SHA", "write_enable": true, "local_umask": "002", "hide_ids": false, "ssl_enable": true, "ipaddress": ""}, "wordpress": {"keys": {"logged_in": {"get_attr": ["wp_logged_in", "value"]}, "secure_auth_key": {"get_attr": ["wp_secure_auth", "value"]}, "nonce_key": {"get_attr": ["wp_nonce", "value"]}, "auth": {"get_attr": ["wp_auth", "value"]}}, "server_aliases": [{"get_param": "domain"}], "version": {"get_param": "version"}, "db": {"host": "127.0.0.1", "user": {"get_param": "username"}, "name": {"get_param": "database_name"}, "pass": {"get_attr": ["database_password", "value"]}}, "dir": {"str_replace": {"params": {"%domain%": {"get_param": "domain"}}, "template": "/var/www/vhosts/%domain%"}}}, "run_list": ["recipe[apt]", "recipe[build-essential]", "recipe[rax-wordpress::apache-prep]", "recipe[sysctl::attribute_driver]", "recipe[mysql::server]", "recipe[rax-wordpress::mysql]", "recipe[hollandbackup]", "recipe[hollandbackup::mysqldump]", "recipe[hollandbackup::main]", "recipe[hollandbackup::backupsets]", "recipe[hollandbackup::cron]", "recipe[rax-wordpress::x509]", "recipe[memcached]", "recipe[php]", "recipe[rax-install-packages]", "recipe[wordpress]", "recipe[rax-wordpress::wp-setup]", "recipe[rax-wordpress::user]", "recipe[rax-wordpress::memcache]", "recipe[lsyncd]", "recipe[vsftpd]", "recipe[rax-wordpress::vsftpd]", "recipe[varnish::repo]", "recipe[varnish]", "recipe[rax-wordpress::apache]", "recipe[rax-wordpress::varnish]", "recipe[rax-wordpress::firewall]", "recipe[rax-wordpress::vsftpd-firewall]", "recipe[rax-wordpress::lsyncd]"], "mysql": {"remove_test_database": true, "server_debian_password": {"get_attr": ["mysql_debian_password", "value"]}, "server_root_password": {"get_attr": ["mysql_root_password", "value"]}, "bind_address": "127.0.0.1", "remove_anonymous_users": true, "server_repl_password": {"get_attr": ["mysql_repl_password", "value"]}}, "apache": {"listen_ports": [8080], "serversignature": "Off", "traceenable": "Off", "timeout": 30}, "memcached": {"listen": "127.0.0.1"}, "hollandbackup": {"main": {"mysqldump": {"host": "localhost", "password": {"get_attr": ["mysql_root_password", "value"]}, "user": "root"}, "backup_directory": "/var/lib/mysqlbackup"}}, "rax": {"apache": {"domain": {"get_param": "domain"}}, "varnish": {"master_backend": "localhost"}, "packages": ["php5-imagick"], "wordpress": {"admin_pass": {"get_attr": ["database_password", "value"]}, "admin_user": {"get_param": "username"}, "user": {"group": {"get_param": "username"}, "name": {"get_param": "username"}}}, "lsyncd": {"ssh": {"private_key": {"get_attr": ["sync_key", "private_key"]}}}}}, "username": "root", "private_key": {"get_attr": ["ssh_key", "private_key"]}, "host": {"get_attr": ["wordpress_server", "accessIPv4"]}, "chef_version": {"get_param": "chef_version"}, "kitchen": {"get_param": "kitchen"}}}, "database_password": {"type": "OS::Heat::RandomString", "properties": {"length": 16, "sequence": "lettersdigits"}}, "wp_logged_in": {"type": "OS::Heat::RandomString", "properties": {"length": 32, "sequence": "hexdigits"}}, "mysql_repl_password": {"type": "OS::Heat::RandomString", "properties": {"length": 16, "sequence": "lettersdigits"}}, "wp_nonce": {"type": "OS::Heat::RandomString", "properties": {"length": 32, "sequence": "hexdigits"}}}}, "action": "UPDATE", "project_id": "883286", "id": "b10bfa80-e495-40d7-bb5a-f663f514c804", "resources": {"sync_key": {"status": "COMPLETE", "name": "sync_key", "resource_data": {"private_key": "-----BEGIN RSA PRIVATE KEY-----\\nMIIEpAIBAAKCAQEAxPfyF/OT4yzSOBmH8yYtC3OB37Kd17jPvpdE0kAuRoWYAcyV\\nCTOn9z9XgmB4wjllC1Jbs/YqHh5m3ygQUMxHES8cf6AoCmH/oM1JdHUFgvRe8W8s\\nDNqUdhuuHRiiV9jD2sv30hnCNtyNJuBPgSYjV0xM0LmY1k2WVFmpLaFf+sd0cIGD\\nfUYcELSdnmgCz2LAESZgkmay1sY0FCpLcorVhTGcw7GNvRpQSApdWpq6D//+0lIL\\npneyUzziX6uYYOuCTxSJVKJk14IyTSakbfgFlrNFLIh5CZme+uCM9o6rDbJgCcMa\\nQdPstwfJbUcCpWC9t4Hl5rA/37/0tWMXITCg7QIDAQABAoIBAQCDU43mylDgNxIy\\ntVMfm2SNLgZ5z+3N1zssKE+Kn6A7BPfEu1LjP73N7D28f/YECaCFW/QomQib7ElK\\noLvAI3N+0Zp+vZn00kJORJGlRCDYn3ZuI2GLcHFsDiiY3cPgLnbnevdQ7ju/uG2k\\nbgqUYYlOu2C8CgMNX83Lj7xs4BvOZ+EDfOY9dAU37D9oahjTNLSR4XpkpsAgrXi0\\nTW+Hqx3MFK9DtVxYqr8+4REzZlxkpSQU5ipTOP6TwxMtKooN8qB5fGaAY3lQIWgH\\n29Oy3tBn2WO948qoZbJqDogVIn9i743ldnEYU5hJ8bWr0NhGdGY6yZDtRjiUipbA\\nXzeMwmFBAoGBAPjn2vMRKcFwoztOAqtvdu+KUD2w2tjR7JgzlcbHf3qFBMwMY6FQ\\nQCyK8S2X/LfMi/H+prxrsaISvm70bTvHBbSjYrts17CQzERcmdlBTvIecskTP6M7\\n4Ht7VU7sjOWfhgFT/5o/qaxgL+D/F4veO21u8Nq6aLfW3a3tLnAz4FJbAoGBAMqV\\nIU3+qGI96kCKdUUEil/oegNZVmSFYTGRPcmhO7FKrsOjH53KRJSLIkdbLeYT0zzD\\nHHTbhA+dYRHt7bRKbUPN1WzPpH7q+LecWaNv2zT9NaMNJeoSznKdcOOnVPwMUQRR\\nECPG5RGT/v/JKtjJIj1aYMscBVFSczlQL3M09yxXAoGAB1pSDXwkT6KUL9xOF+Jj\\nERB07l2bGWyaIKTld8nM6kGjsqNrDgjg3G/+T+p9fLB+Mdfj9Qz5YmBLX9u4nlty\\nv7NT51V/yad9YUebA9/6BQ0BNw9qgdfy+bLbAknan63mt4NTuarHyF/PCkZ+25Ll\\nDoaIdu2qykN+qPSouofNyKECgYBpaDcwEfUjSPv+IQzroHUvehMicvWU0CHGXMA9\\njXs1wJo2iUYGIByW/d4UKskzEdWzpAHGfAG27jh3z8kDKka4JP2L5G6+6xwGzX+G\\nnsj8RVQHRuwXYzmwQWNf0M1TaEUvbc5sDy1ZfBwOk2mL6vu52LDMfgP2UGRLygEm\\nfMSveQKBgQCEXBICU51DmMtkkshrbZuvYyNQ+vZ7D6mGLZcF7rzcYBwhieDs6jDq\\n5yfD/WmtNHPER7vgSekXsB0Z9QPN3FAKhhXUNeIFH0780P+vnR8iuCc1p4QmySGW\\nJi/fF1kCdJKTYlFtGSd/Q6PELn6brD41lVnm/MCfYGw7Q06zdxDnHg==\\n-----END RSA PRIVATE KEY-----\\n"}, "resource_id": "b10bfa80-e495-40d7-bb5a-f663f514c804-sync", "action": "CREATE", "type": "OS::Nova::KeyPair", "metadata": {}}, "wp_secure_auth": {"status": "COMPLETE", "name": "wp_secure_auth", "resource_data": {"value": "30BA76B73A52FAC6DBEBE265AD6C2617"}, "resource_id": "30BA76B73A52FAC6DBEBE265AD6C2617", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}, "wordpress_server": {"status": "COMPLETE", "name": "wordpress_server", "resource_data": {"private_key": "-----BEGIN RSA PRIVATE KEY-----\\nMIICXAIBAAKBgQDlcT+x9kDr/J9cd3G9ep9T6UPCGGCunB+h1xO2SuJdwe5AJkPc\\nDPWT/BGncIyq5PdHwIB9w/PNRbe015GvdMh9ToIK539G2gv/F8denVLv5VRRPL2k\\nmO5uCn273LqK4kiuTP65WQWj+HDpQBAiB6r2VQh0S4DR1JadmbR2c5clhwIDAQAB\\nAoGAAdzNe5BYLpI6aPG/Rp58NJ4sIqM4BbLWvuWUD2LEO6abXIHzAxJH3A+rxQQw\\n4CJDr51sbZjtnbj3KMynLhlwly/ghZrP+a7fwwD6S30W/8qItzfO3YFLbTxEUhK4\\nOU3oMNMgRGq6shuKkYJVwt4fKESpDmryxcZr3TOFyvsffyECQQDuVOB1yuQE1ulE\\nL+9lUz3evtSNOyrDD8pu75UftJ9rcObTuk470Vc/gl5YmaymOuV6GDExjG1DR4k5\\nr0BJG/+7AkEA9nOruhZQI23tDLYBzO/fe8DqJdh16KtgYvyqFmJMmrHkrLYzxwPG\\n1XqMZO031807SfC0qb4mZiydVPSbvX/WpQJAFM4R/hZlC0sbd9lbY5P9rako8t88\\nX2TMfhyp/ueMlxt2+vqjg7NFk4S06bUYjjZL+/mKqdGhZCMlhoSW7wrjqwJBAOZi\\nGxZJ5YA5Mm+/dM9vLSsym6/lOdPW4LOoHhfurE2wHmSVrrFMBoNpm/R9DMbfQ51L\\nNpe2+Y5qBml0gGIVL0ECQBHoLdqvn/zuL9zWDshdjcdu2dKaQtImMyC7DGx/ouNG\\nw6kTXE6vwCIBhcXbipSa3MyH+If78m4tqGcnCh6PqGI=\\n-----END RSA PRIVATE KEY-----"}, "resource_id": "e45541dc-7d6c-4ada-bdd6-b6e8c27c7d2b", "action": "CREATE", "type": "Rackspace::Cloud::Server", "metadata": {}}, "mysql_root_password": {"status": "COMPLETE", "name": "mysql_root_password", "resource_data": {"value": "xmBpiAQU5a3q9lsF"}, "resource_id": "xmBpiAQU5a3q9lsF", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}, "mysql_debian_password": {"status": "COMPLETE", "name": "mysql_debian_password", "resource_data": {"value": "kOIKVAaIpItvS8yM"}, "resource_id": "kOIKVAaIpItvS8yM", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}, "ssh_key": {"status": "COMPLETE", "name": "ssh_key", "resource_data": {"private_key": "-----BEGIN RSA PRIVATE KEY-----\\nMIIEpAIBAAKCAQEAwwWQFqJWvP+0mRhnJSHQIDNEj9BFskQLe2n++0SZgGP7fb22\\nw3DtjZ9iSKQ2tFJmCb3OscZQDZx+IG/PtFD/GbDgSZHA6hBzgYMFEkW1fSHj/g2Y\\n2W3FQplxBIA9uBV62M+ILpn1xw/SLQgFvbBzetOpr6/mMiswLUqxVdc53KxnAF/F\\nXbfThSFfGtLb6z7DA7MP1J7SVqz6xggtCUGYzudLYm4DTIj3TPkloyXuFdLpb4+R\\nqhmRpSq9Jt02ZUsPMdg9Jqhk9CeFhkZFsy7SBS+NsfiB++wVAIQF7VtE0gFk3WwC\\nsU6gwpMSYTFxf9i4ovyrBgLZ2Vc73IBFrRx8zwIDAQABAoIBAB4skiquW3VKqwq0\\n9+CK5sTUqdsGgoIefRhPQiBmcMmorpS58bkzk83Bx1ct8TjdNuRy9bQT1vcEK4+h\\nPSXNEmtLLqizYIHWoch8GSDGoFoIEFqSh/+8ODUhwJbNsL72s9cv5QYw1BJEpGRL\\nRXggAP4UGcERGjDQ9ddMIzwA3PcDgJaTJ/O9umzdTGiQsXDOYW7YGJNS6akZPkhr\\nbccLIzUA/PkAZdf+j6Q9zzWE1cBHYwZ6e/HcqIy7ElIvctvnVPL1Oizsnt7/lVz7\\n7KgQcT0VB4UiADJJrBbQjChUpuldeoZi3IYUDRmPrYBWLSELVFok/jD2AKViqaoV\\n464xYgECgYEA4e3bHLMgfQnCqvt4Pzy7hcof31Rbra4/2//zRCNDg8V5JWxNh3dh\\nWx9A5W24evuMU7Zu62eiYXuASUZt6ZxsIgETkCm540MKBMSfqDcFRSydRDmUEw25\\nN8An7639HluOkF8PlYl8PtfQLdMAHsaa9/s6+uqyRJdZGIRDKzi9UQ8CgYEA3PqX\\nRwpid6QTCGYeEhc9ZrMF0szseOFPJJbG5Jg1xQ1dIfkFWPuE7jWpN74pZ0JWqMMw\\nI+CyGmpoVKPmPD1AqN2z4idGeIMA6iv08GUcFgw4F1OYToGxPS0OJsl/F0OKqmLB\\nvjlHJK2++l47fFl+psP/r1m4J4BRk59YH4B2mEECgYEAmW5qHmx7xM7LGEkdGX0K\\nMMraqFVmyWWL0sFYmM6F/EgwhLyvTi9Bu5tW/DhuT37jhrpfS5keyqsPrTOaU0s6\\nmEE44u+jYPZXKHPLpXZwKtEooHul1ua8AWOK+5eiTWqKP/t+3uP2r8rqgyRHcZ8Z\\nAQ3puRuII1LRW/f+kay/zPsCgYAQZM7gSFbxxUxcLSdB9FNr0RA3iVhpx11Vu5HZ\\n16j1i35DTPQmm9JK0dRR/FuZ+4PuVTy3DK5p40cGMHqeMXUgkgIMXxmNSzrAJK6x\\nPu8Me6+Vm3ALMvfxL+yC2CQDl9ErvtPcxucOQ42NiXwkR4dr29KWMbPFynFC4Glr\\nPN6PgQKBgQDK89IhMt3IeSUcBl4oEKpCrKPOapbIlEETCVCNAMesB1lnr7qGGJNZ\\nWXHiNzJ207NeXfNxvnnn4MgR7EnZR0U3rxco5danwBQ05VUfApL3mqXcTJMl2ntV\\nJpNLjtqJJgu7trxFpo2PCXFPQHKDitDiBi9WSE4jqqTu7uJNSq7KrA==\\n-----END RSA PRIVATE KEY-----\\n"}, "resource_id": "b10bfa80-e495-40d7-bb5a-f663f514c804", "action": "CREATE", "type": "OS::Nova::KeyPair", "metadata": {}}, "wp_auth": {"status": "COMPLETE", "name": "wp_auth", "resource_data": {"value": "2F8369B266B2C92CF7A1A5DB841443F3"}, "resource_id": "2F8369B266B2C92CF7A1A5DB841443F3", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}, "wordpress_setup": {"status": "COMPLETE", "name": "wordpress_setup", "resource_data": {"process_id": "24089"}, "resource_id": "8cc78f9d-4066-4f6c-9876-ace25ca83f30", "action": "CREATE", "type": "OS::Heat::ChefSolo", "metadata": {}}, "database_password": {"status": "COMPLETE", "name": "database_password", "resource_data": {"value": "TPAGoiCwash9T1fi"}, "resource_id": "TPAGoiCwash9T1fi", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}, "wp_logged_in": {"status": "COMPLETE", "name": "wp_logged_in", "resource_data": {"value": "026611BAE58FDE37C69E2F2EDB563EB2"}, "resource_id": "026611BAE58FDE37C69E2F2EDB563EB2", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}, "mysql_repl_password": {"status": "COMPLETE", "name": "mysql_repl_password", "resource_data": {"value": "3kRxPiIAt8xksyXA"}, "resource_id": "3kRxPiIAt8xksyXA", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}, "wp_nonce": {"status": "COMPLETE", "name": "wp_nonce", "resource_data": {"value": "705CC92E02C3F6877C27EFD5B4925D0F"}, "resource_id": "705CC92E02C3F6877C27EFD5B4925D0F", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}}}
"""

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

    def test_all(self):
        self._test_stack()

    @attr(type='smoke')
    def _test_stack(self, template=None):

        print os.environ.get('TEMPEST_CONFIG')
        if os.environ.get('TEMPEST_CONFIG') == None:
            print "Set the environment varible TEMPEST_CONFIG to a config file."
            self.fail("Environment variable is not set.")

        env = self.config.orchestration['env']
        account = self.config.identity['username']

        print template

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

        # env = self.config.orchestration['env']
        # #env = "dev"
        # template_giturl = "https://raw2.github.com/heat-ci/heat-templates/master/" + env + "/" + template + ".template"
        # #print template_giturl
        # response_templates = requests.get(template_giturl, timeout=3)
        # yaml_template = yaml.safe_load(response_templates.content)
        # #print yaml_template

        parameters = {}
        if 'key_name' in yaml_template['parameters']:
            parameters = {
                'key_name': 'sabeen'
            }
        if 'git_url' in yaml_template['parameters']:
            parameters['git_url'] = "https://github.com/timductive/phphelloworld"
            #https://github.com/beenzsyed/phphelloworld

        #region = "Dev"
        #rstype = "Rackspace::Cloud::Server"
        #rsname = "devstack_server"

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

            #stack-list - doing this again because it has known to fail if called after a stack create
            apiname = "stack list"
            slresp, stacklist = self.orchestration_client.list_stacks(region)
            self._check_resp(slresp, stacklist, apiname)

            #update stack
            apiname = "update stack"
            parameters = {
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
            asresp, asbody, stack_identifier = self.adopt_stack(adopt_stack_name, region, adopt_data2, yaml_template, parameters)
            self._check_resp(asresp, asbody, apiname)


            #--------  Stack resources  --------
            #Lists resources in a stack
            apiname = "list resources"
            if updateStackName != 0:
                lrresp, lrbody = self.orchestration_client.list_resources(updateStackName, updateStackId, region)
                self._check_resp(lrresp, lrbody, apiname)

            #Gets metadata for a specified resource.
            apiname = "resource metadata"
            if updateStackName != 0:
                rs_name = self._get_resource_name(lrbody)
                rmresp, rmbody = self.orchestration_client.show_resource_metadata(updateStackName, updateStackId, rs_name, region)
                self._check_resp(rmresp, rmbody, apiname)

            #Gets data for a specified resource.
            apiname = "get resources"
            if updateStackName != 0:
                rsresp, rsbody = self.orchestration_client.get_resource(updateStackName, updateStackId, rs_name, region)
                self._check_resp(rsresp, rsbody, apiname)

            #Gets a template representation for a specified resource type.
            apiname = "resource template"
            rs_type = self._get_resource_type(lrbody)
            rtresp, rtbody = self.orchestration_client.resource_template(rs_type, region)
            self._check_resp(rtresp, rtbody, apiname)

            #Lists the supported template resource types.
            apiname = "template resource types"
            rtresp, rtbody = self.orchestration_client.template_resource(region)
            self._check_resp(rtresp, rtbody, apiname)

            #Gets the interface schema for a specified resource type.
            apiname = "schema for resource type"
            rtresp, rtbody = self.orchestration_client.resource_schema(rs_type, region)
            self._check_resp(rtresp, rtbody, apiname)


            #-------  Stack events  ----------
            #event list
            apiname = "list event"
            if updateStackName != 0:
                evresp, evbody = self.orchestration_client.list_events(updateStackName, updateStackId, region)
                self._check_resp(evresp, evbody, apiname)

            #event show
            apiname = "show event"
            if updateStackName != 0:
                event_id, rs_name_event = self._get_event_id(evbody)
                esresp, esbody = self.orchestration_client.show_event(updateStackName, updateStackId, rs_name_event, event_id, region)
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
            return stackname['id'], stackname['resource_name']

    def _get_resource_name(self, body):
        for resource in body:
            return resource['resource_name']

    def _get_resource_type(self, body):
        for resource in body:
            return resource['resource_type']




