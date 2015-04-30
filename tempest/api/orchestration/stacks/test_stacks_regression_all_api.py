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
from httplib import BadStatusLine
import ipdb


LOG = logging.getLogger(__name__)

adopt_data2 = """
{"status": "COMPLETE", "name": "ADOPT_554748", "stack_user_project_id": "883286", "environment": {"parameters": {"server_hostname": "WordPress", "username": "wp_user", "domain": "example1234.com", "image": "Ubuntu 12.04 LTS (Precise Pangolin) (PVHVM)", "chef_version": "11.16.2", "prefix": "wp_", "version": "3.9.2", "flavor": "2 GB Performance", "database_name": "wordpress", "kitchen": "https://github.com/rackspace-orchestration-templates/wordpress-single.git"}, "resource_registry": {"resources": {}}}, "template": {"parameter_groups": [{"parameters": ["server_hostname", "image", "flavor"], "label": "Server Settings"}, {"parameters": ["domain", "username"], "label": "WordPress Settings"}, {"parameters": ["kitchen", "chef_version", "version", "prefix"], "label": "rax-dev-params"}], "heat_template_version": "2013-05-23", "description": "This is a Heat template to deploy a single Linux server running WordPress.\\n", "parameters": {"server_hostname": {"default": "WordPress", "label": "Server Name", "type": "string", "description": "Hostname to use for the server that\'s built.", "constraints": [{"length": {"max": 64, "min": 1}}, {"allowed_pattern": "^[a-zA-Z][a-zA-Z0-9-]*$", "description": "Must begin with a letter and contain only alphanumeric characters.\\n"}]}, "username": {"default": "wp_user", "label": "Username", "type": "string", "description": "Username for system, database, and WordPress logins.", "constraints": [{"allowed_pattern": "^[a-zA-Z0-9 _.@-]{1,16}$", "description": "Must be shorter than 16 characters and may only contain alphanumeric\\ncharacters, \' \', \'_\', \'.\', \'@\', and/or \'-\'.\\n"}]}, "domain": {"default": "example.com", "label": "Site Domain", "type": "string", "description": "Domain to be used with WordPress site", "constraints": [{"allowed_pattern": "^[a-zA-Z0-9.-]{1,255}.[a-zA-Z]{2,15}$", "description": "Must be a valid domain name"}]}, "database_name": {"default": "wordpress", "label": "Database Name", "type": "string", "description": "WordPress database name", "constraints": [{"allowed_pattern": "^[0-9a-zA-Z$_]{1,64}$", "description": "Maximum length of 64 characters, may only contain letters, numbers, and\\nunderscores.\\n"}]}, "chef_version": {"default": "11.16.2", "type": "string", "description": "Version of chef client to use", "label": "Chef Version"}, "prefix": {"default": "wp_", "label": "Database Prefix", "type": "string", "description": "Prefix to use for WordPress database tables", "constraints": [{"allowed_pattern": "^[0-9a-zA-Z$_]{0,10}$", "description": "Prefix must be shorter than 10 characters, and can only include\\nletters, numbers, $, and/or underscores.\\n"}]}, "version": {"default": "3.9.2", "label": "WordPress Version", "type": "string", "description": "Version of WordPress to install", "constraints": [{"allowed_values": ["3.9.2"]}]}, "flavor": {"default": "1 GB Performance", "label": "Server Size", "type": "string", "description": "Required: Rackspace Cloud Server flavor to use. The size is based on the\\namount of RAM for the provisioned server.\\n", "constraints": [{"description": "Must be a valid Rackspace Cloud Server flavor for the region you have\\nselected to deploy into.\\n", "allowed_values": ["1 GB Performance", "2 GB Performance", "4 GB Performance", "8 GB Performance", "15 GB Performance", "30 GB Performance", "1GB Standard Instance", "2GB Standard Instance", "4GB Standard Instance", "8GB Standard Instance", "15GB Standard Instance", "30GB Standard Instance"]}]}, "image": {"default": "Ubuntu 12.04 LTS (Precise Pangolin) (PVHVM)", "label": "Operating System", "type": "string", "description": "Required: Server image used for all servers that are created as a part of\\nthis deployment.\\n", "constraints": [{"description": "Must be a supported operating system.", "allowed_values": ["Ubuntu 12.04 LTS (Precise Pangolin)"]}]}, "kitchen": {"default": "https://github.com/rackspace-orchestration-templates/wordpress-single.git", "type": "string", "description": "URL for a git repo containing required cookbooks", "label": "Kitchen URL"}}, "outputs": {"mysql_root_password": {"description": "MySQL Root Password", "value": {"get_attr": ["mysql_root_password", "value"]}}, "wordpress_password": {"description": "WordPress Password", "value": {"get_attr": ["database_password", "value"]}}, "private_key": {"description": "SSH Private Key", "value": {"get_attr": ["ssh_key", "private_key"]}}, "server_ip": {"description": "Server IP", "value": {"get_attr": ["wordpress_server", "accessIPv4"]}}, "wordpress_user": {"description": "WordPress User", "value": {"get_param": "username"}}}, "resources": {"sync_key": {"type": "OS::Nova::KeyPair", "properties": {"name": {"str_replace": {"params": {"%stack_id%": {"get_param": "OS::stack_id"}}, "template": "%stack_id%-sync"}}, "save_private_key": true}}, "wp_secure_auth": {"type": "OS::Heat::RandomString", "properties": {"length": 32, "sequence": "hexdigits"}}, "wordpress_server": {"type": "Rackspace::Cloud::Server", "properties": {"key_name": {"get_resource": "ssh_key"}, "flavor": {"get_param": "flavor"}, "image": {"get_param": "image"}, "name": {"get_param": "server_hostname"}, "metadata": {"rax-heat": {"get_param": "OS::stack_id"}}}}, "mysql_root_password": {"type": "OS::Heat::RandomString", "properties": {"length": 16, "sequence": "lettersdigits"}}, "mysql_debian_password": {"type": "OS::Heat::RandomString", "properties": {"length": 16, "sequence": "lettersdigits"}}, "ssh_key": {"type": "OS::Nova::KeyPair", "properties": {"name": {"get_param": "OS::stack_id"}, "save_private_key": true}}, "wp_auth": {"type": "OS::Heat::RandomString", "properties": {"length": 32, "sequence": "hexdigits"}}, "wordpress_setup": {"depends_on": "wordpress_server", "type": "OS::Heat::ChefSolo", "properties": {"node": {"varnish": {"version": "3.0", "listen_port": "80"}, "sysctl": {"values": {"fs.inotify.max_user_watches": 1000000}}, "lsyncd": {"interval": 5}, "monit": {"mail_format": {"from": "monit@localhost"}, "notify_email": "root@localhost"}, "vsftpd": {"chroot_local_user": false, "ssl_ciphers": "AES256-SHA", "write_enable": true, "local_umask": "002", "hide_ids": false, "ssl_enable": true, "ipaddress": ""}, "wordpress": {"keys": {"logged_in": {"get_attr": ["wp_logged_in", "value"]}, "secure_auth_key": {"get_attr": ["wp_secure_auth", "value"]}, "nonce_key": {"get_attr": ["wp_nonce", "value"]}, "auth": {"get_attr": ["wp_auth", "value"]}}, "server_aliases": [{"get_param": "domain"}], "version": {"get_param": "version"}, "db": {"host": "127.0.0.1", "user": {"get_param": "username"}, "name": {"get_param": "database_name"}, "pass": {"get_attr": ["database_password", "value"]}}, "dir": {"str_replace": {"params": {"%domain%": {"get_param": "domain"}}, "template": "/var/www/vhosts/%domain%"}}}, "run_list": ["recipe[apt]", "recipe[build-essential]", "recipe[rax-wordpress::apache-prep]", "recipe[sysctl::attribute_driver]", "recipe[mysql::server]", "recipe[rax-wordpress::mysql]", "recipe[hollandbackup]", "recipe[hollandbackup::mysqldump]", "recipe[hollandbackup::main]", "recipe[hollandbackup::backupsets]", "recipe[hollandbackup::cron]", "recipe[rax-wordpress::x509]", "recipe[memcached]", "recipe[php]", "recipe[rax-install-packages]", "recipe[wordpress]", "recipe[rax-wordpress::wp-setup]", "recipe[rax-wordpress::user]", "recipe[rax-wordpress::memcache]", "recipe[lsyncd]", "recipe[vsftpd]", "recipe[rax-wordpress::vsftpd]", "recipe[varnish::repo]", "recipe[varnish]", "recipe[rax-wordpress::apache]", "recipe[rax-wordpress::varnish]", "recipe[rax-wordpress::firewall]", "recipe[rax-wordpress::vsftpd-firewall]", "recipe[rax-wordpress::lsyncd]"], "mysql": {"remove_test_database": true, "server_debian_password": {"get_attr": ["mysql_debian_password", "value"]}, "server_root_password": {"get_attr": ["mysql_root_password", "value"]}, "bind_address": "127.0.0.1", "remove_anonymous_users": true, "server_repl_password": {"get_attr": ["mysql_repl_password", "value"]}}, "apache": {"listen_ports": [8080], "serversignature": "Off", "traceenable": "Off", "timeout": 30}, "memcached": {"listen": "127.0.0.1"}, "hollandbackup": {"main": {"mysqldump": {"host": "localhost", "password": {"get_attr": ["mysql_root_password", "value"]}, "user": "root"}, "backup_directory": "/var/lib/mysqlbackup"}}, "rax": {"apache": {"domain": {"get_param": "domain"}}, "varnish": {"master_backend": "localhost"}, "packages": ["php5-imagick"], "wordpress": {"admin_pass": {"get_attr": ["database_password", "value"]}, "admin_user": {"get_param": "username"}, "user": {"group": {"get_param": "username"}, "name": {"get_param": "username"}}}, "lsyncd": {"ssh": {"private_key": {"get_attr": ["sync_key", "private_key"]}}}}}, "username": "root", "private_key": {"get_attr": ["ssh_key", "private_key"]}, "host": {"get_attr": ["wordpress_server", "accessIPv4"]}, "chef_version": {"get_param": "chef_version"}, "kitchen": {"get_param": "kitchen"}}}, "database_password": {"type": "OS::Heat::RandomString", "properties": {"length": 16, "sequence": "lettersdigits"}}, "wp_logged_in": {"type": "OS::Heat::RandomString", "properties": {"length": 32, "sequence": "hexdigits"}}, "mysql_repl_password": {"type": "OS::Heat::RandomString", "properties": {"length": 16, "sequence": "lettersdigits"}}, "wp_nonce": {"type": "OS::Heat::RandomString", "properties": {"length": 32, "sequence": "hexdigits"}}}}, "action": "UPDATE", "project_id": "883286", "id": "b10bfa80-e495-40d7-bb5a-f663f514c804", "resources": {"sync_key": {"status": "COMPLETE", "name": "sync_key", "resource_data": {"private_key": "-----BEGIN RSA PRIVATE KEY-----\\nMIIEpAIBAAKCAQEAxPfyF/OT4yzSOBmH8yYtC3OB37Kd17jPvpdE0kAuRoWYAcyV\\nCTOn9z9XgmB4wjllC1Jbs/YqHh5m3ygQUMxHES8cf6AoCmH/oM1JdHUFgvRe8W8s\\nDNqUdhuuHRiiV9jD2sv30hnCNtyNJuBPgSYjV0xM0LmY1k2WVFmpLaFf+sd0cIGD\\nfUYcELSdnmgCz2LAESZgkmay1sY0FCpLcorVhTGcw7GNvRpQSApdWpq6D//+0lIL\\npneyUzziX6uYYOuCTxSJVKJk14IyTSakbfgFlrNFLIh5CZme+uCM9o6rDbJgCcMa\\nQdPstwfJbUcCpWC9t4Hl5rA/37/0tWMXITCg7QIDAQABAoIBAQCDU43mylDgNxIy\\ntVMfm2SNLgZ5z+3N1zssKE+Kn6A7BPfEu1LjP73N7D28f/YECaCFW/QomQib7ElK\\noLvAI3N+0Zp+vZn00kJORJGlRCDYn3ZuI2GLcHFsDiiY3cPgLnbnevdQ7ju/uG2k\\nbgqUYYlOu2C8CgMNX83Lj7xs4BvOZ+EDfOY9dAU37D9oahjTNLSR4XpkpsAgrXi0\\nTW+Hqx3MFK9DtVxYqr8+4REzZlxkpSQU5ipTOP6TwxMtKooN8qB5fGaAY3lQIWgH\\n29Oy3tBn2WO948qoZbJqDogVIn9i743ldnEYU5hJ8bWr0NhGdGY6yZDtRjiUipbA\\nXzeMwmFBAoGBAPjn2vMRKcFwoztOAqtvdu+KUD2w2tjR7JgzlcbHf3qFBMwMY6FQ\\nQCyK8S2X/LfMi/H+prxrsaISvm70bTvHBbSjYrts17CQzERcmdlBTvIecskTP6M7\\n4Ht7VU7sjOWfhgFT/5o/qaxgL+D/F4veO21u8Nq6aLfW3a3tLnAz4FJbAoGBAMqV\\nIU3+qGI96kCKdUUEil/oegNZVmSFYTGRPcmhO7FKrsOjH53KRJSLIkdbLeYT0zzD\\nHHTbhA+dYRHt7bRKbUPN1WzPpH7q+LecWaNv2zT9NaMNJeoSznKdcOOnVPwMUQRR\\nECPG5RGT/v/JKtjJIj1aYMscBVFSczlQL3M09yxXAoGAB1pSDXwkT6KUL9xOF+Jj\\nERB07l2bGWyaIKTld8nM6kGjsqNrDgjg3G/+T+p9fLB+Mdfj9Qz5YmBLX9u4nlty\\nv7NT51V/yad9YUebA9/6BQ0BNw9qgdfy+bLbAknan63mt4NTuarHyF/PCkZ+25Ll\\nDoaIdu2qykN+qPSouofNyKECgYBpaDcwEfUjSPv+IQzroHUvehMicvWU0CHGXMA9\\njXs1wJo2iUYGIByW/d4UKskzEdWzpAHGfAG27jh3z8kDKka4JP2L5G6+6xwGzX+G\\nnsj8RVQHRuwXYzmwQWNf0M1TaEUvbc5sDy1ZfBwOk2mL6vu52LDMfgP2UGRLygEm\\nfMSveQKBgQCEXBICU51DmMtkkshrbZuvYyNQ+vZ7D6mGLZcF7rzcYBwhieDs6jDq\\n5yfD/WmtNHPER7vgSekXsB0Z9QPN3FAKhhXUNeIFH0780P+vnR8iuCc1p4QmySGW\\nJi/fF1kCdJKTYlFtGSd/Q6PELn6brD41lVnm/MCfYGw7Q06zdxDnHg==\\n-----END RSA PRIVATE KEY-----\\n"}, "resource_id": "b10bfa80-e495-40d7-bb5a-f663f514c804-sync", "action": "CREATE", "type": "OS::Nova::KeyPair", "metadata": {}}, "wp_secure_auth": {"status": "COMPLETE", "name": "wp_secure_auth", "resource_data": {"value": "30BA76B73A52FAC6DBEBE265AD6C2617"}, "resource_id": "30BA76B73A52FAC6DBEBE265AD6C2617", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}, "wordpress_server": {"status": "COMPLETE", "name": "wordpress_server", "resource_data": {"private_key": "-----BEGIN RSA PRIVATE KEY-----\\nMIICXAIBAAKBgQDlcT+x9kDr/J9cd3G9ep9T6UPCGGCunB+h1xO2SuJdwe5AJkPc\\nDPWT/BGncIyq5PdHwIB9w/PNRbe015GvdMh9ToIK539G2gv/F8denVLv5VRRPL2k\\nmO5uCn273LqK4kiuTP65WQWj+HDpQBAiB6r2VQh0S4DR1JadmbR2c5clhwIDAQAB\\nAoGAAdzNe5BYLpI6aPG/Rp58NJ4sIqM4BbLWvuWUD2LEO6abXIHzAxJH3A+rxQQw\\n4CJDr51sbZjtnbj3KMynLhlwly/ghZrP+a7fwwD6S30W/8qItzfO3YFLbTxEUhK4\\nOU3oMNMgRGq6shuKkYJVwt4fKESpDmryxcZr3TOFyvsffyECQQDuVOB1yuQE1ulE\\nL+9lUz3evtSNOyrDD8pu75UftJ9rcObTuk470Vc/gl5YmaymOuV6GDExjG1DR4k5\\nr0BJG/+7AkEA9nOruhZQI23tDLYBzO/fe8DqJdh16KtgYvyqFmJMmrHkrLYzxwPG\\n1XqMZO031807SfC0qb4mZiydVPSbvX/WpQJAFM4R/hZlC0sbd9lbY5P9rako8t88\\nX2TMfhyp/ueMlxt2+vqjg7NFk4S06bUYjjZL+/mKqdGhZCMlhoSW7wrjqwJBAOZi\\nGxZJ5YA5Mm+/dM9vLSsym6/lOdPW4LOoHhfurE2wHmSVrrFMBoNpm/R9DMbfQ51L\\nNpe2+Y5qBml0gGIVL0ECQBHoLdqvn/zuL9zWDshdjcdu2dKaQtImMyC7DGx/ouNG\\nw6kTXE6vwCIBhcXbipSa3MyH+If78m4tqGcnCh6PqGI=\\n-----END RSA PRIVATE KEY-----"}, "resource_id": "e45541dc-7d6c-4ada-bdd6-b6e8c27c7d2b", "action": "CREATE", "type": "Rackspace::Cloud::Server", "metadata": {}}, "mysql_root_password": {"status": "COMPLETE", "name": "mysql_root_password", "resource_data": {"value": "xmBpiAQU5a3q9lsF"}, "resource_id": "xmBpiAQU5a3q9lsF", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}, "mysql_debian_password": {"status": "COMPLETE", "name": "mysql_debian_password", "resource_data": {"value": "kOIKVAaIpItvS8yM"}, "resource_id": "kOIKVAaIpItvS8yM", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}, "ssh_key": {"status": "COMPLETE", "name": "ssh_key", "resource_data": {"private_key": "-----BEGIN RSA PRIVATE KEY-----\\nMIIEpAIBAAKCAQEAwwWQFqJWvP+0mRhnJSHQIDNEj9BFskQLe2n++0SZgGP7fb22\\nw3DtjZ9iSKQ2tFJmCb3OscZQDZx+IG/PtFD/GbDgSZHA6hBzgYMFEkW1fSHj/g2Y\\n2W3FQplxBIA9uBV62M+ILpn1xw/SLQgFvbBzetOpr6/mMiswLUqxVdc53KxnAF/F\\nXbfThSFfGtLb6z7DA7MP1J7SVqz6xggtCUGYzudLYm4DTIj3TPkloyXuFdLpb4+R\\nqhmRpSq9Jt02ZUsPMdg9Jqhk9CeFhkZFsy7SBS+NsfiB++wVAIQF7VtE0gFk3WwC\\nsU6gwpMSYTFxf9i4ovyrBgLZ2Vc73IBFrRx8zwIDAQABAoIBAB4skiquW3VKqwq0\\n9+CK5sTUqdsGgoIefRhPQiBmcMmorpS58bkzk83Bx1ct8TjdNuRy9bQT1vcEK4+h\\nPSXNEmtLLqizYIHWoch8GSDGoFoIEFqSh/+8ODUhwJbNsL72s9cv5QYw1BJEpGRL\\nRXggAP4UGcERGjDQ9ddMIzwA3PcDgJaTJ/O9umzdTGiQsXDOYW7YGJNS6akZPkhr\\nbccLIzUA/PkAZdf+j6Q9zzWE1cBHYwZ6e/HcqIy7ElIvctvnVPL1Oizsnt7/lVz7\\n7KgQcT0VB4UiADJJrBbQjChUpuldeoZi3IYUDRmPrYBWLSELVFok/jD2AKViqaoV\\n464xYgECgYEA4e3bHLMgfQnCqvt4Pzy7hcof31Rbra4/2//zRCNDg8V5JWxNh3dh\\nWx9A5W24evuMU7Zu62eiYXuASUZt6ZxsIgETkCm540MKBMSfqDcFRSydRDmUEw25\\nN8An7639HluOkF8PlYl8PtfQLdMAHsaa9/s6+uqyRJdZGIRDKzi9UQ8CgYEA3PqX\\nRwpid6QTCGYeEhc9ZrMF0szseOFPJJbG5Jg1xQ1dIfkFWPuE7jWpN74pZ0JWqMMw\\nI+CyGmpoVKPmPD1AqN2z4idGeIMA6iv08GUcFgw4F1OYToGxPS0OJsl/F0OKqmLB\\nvjlHJK2++l47fFl+psP/r1m4J4BRk59YH4B2mEECgYEAmW5qHmx7xM7LGEkdGX0K\\nMMraqFVmyWWL0sFYmM6F/EgwhLyvTi9Bu5tW/DhuT37jhrpfS5keyqsPrTOaU0s6\\nmEE44u+jYPZXKHPLpXZwKtEooHul1ua8AWOK+5eiTWqKP/t+3uP2r8rqgyRHcZ8Z\\nAQ3puRuII1LRW/f+kay/zPsCgYAQZM7gSFbxxUxcLSdB9FNr0RA3iVhpx11Vu5HZ\\n16j1i35DTPQmm9JK0dRR/FuZ+4PuVTy3DK5p40cGMHqeMXUgkgIMXxmNSzrAJK6x\\nPu8Me6+Vm3ALMvfxL+yC2CQDl9ErvtPcxucOQ42NiXwkR4dr29KWMbPFynFC4Glr\\nPN6PgQKBgQDK89IhMt3IeSUcBl4oEKpCrKPOapbIlEETCVCNAMesB1lnr7qGGJNZ\\nWXHiNzJ207NeXfNxvnnn4MgR7EnZR0U3rxco5danwBQ05VUfApL3mqXcTJMl2ntV\\nJpNLjtqJJgu7trxFpo2PCXFPQHKDitDiBi9WSE4jqqTu7uJNSq7KrA==\\n-----END RSA PRIVATE KEY-----\\n"}, "resource_id": "b10bfa80-e495-40d7-bb5a-f663f514c804", "action": "CREATE", "type": "OS::Nova::KeyPair", "metadata": {}}, "wp_auth": {"status": "COMPLETE", "name": "wp_auth", "resource_data": {"value": "2F8369B266B2C92CF7A1A5DB841443F3"}, "resource_id": "2F8369B266B2C92CF7A1A5DB841443F3", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}, "wordpress_setup": {"status": "COMPLETE", "name": "wordpress_setup", "resource_data": {"process_id": "24089"}, "resource_id": "8cc78f9d-4066-4f6c-9876-ace25ca83f30", "action": "CREATE", "type": "OS::Heat::ChefSolo", "metadata": {}}, "database_password": {"status": "COMPLETE", "name": "database_password", "resource_data": {"value": "TPAGoiCwash9T1fi"}, "resource_id": "TPAGoiCwash9T1fi", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}, "wp_logged_in": {"status": "COMPLETE", "name": "wp_logged_in", "resource_data": {"value": "026611BAE58FDE37C69E2F2EDB563EB2"}, "resource_id": "026611BAE58FDE37C69E2F2EDB563EB2", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}, "mysql_repl_password": {"status": "COMPLETE", "name": "mysql_repl_password", "resource_data": {"value": "3kRxPiIAt8xksyXA"}, "resource_id": "3kRxPiIAt8xksyXA", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}, "wp_nonce": {"status": "COMPLETE", "name": "wp_nonce", "resource_data": {"value": "705CC92E02C3F6877C27EFD5B4925D0F"}, "resource_id": "705CC92E02C3F6877C27EFD5B4925D0F", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}}}
"""

adopt_data3 = """
{"status": "COMPLETE", "name": "ADOPT_98324", "stack_user_project_id": "897502", "environment": {"parameter_defaults": {}, "parameters": {"username": "wp_user", "domain": "example.com", "chef_version": "11.16.2", "wp_web_server_flavor": "2 GB General Purpose v1", "wp_web_server_hostnames": "WordPress-Web%index%", "image": "Ubuntu 12.04 LTS (Precise Pangolin) (PVHVM)", "load_balancer_hostname": "WordPress-Load-Balancer", "child_template": "https://raw.githubusercontent.com/rackspace-orchestration-templates/wordpress-multi/master/wordpress-web-server.yaml", "wp_master_server_hostname": "WordPress-Master", "prefix": "wp_", "version": "3.9.2", "wp_master_server_flavor": "2 GB General Purpose v1", "database_name": "wordpress", "wp_web_server_count": "1", "database_server_flavor": "4 GB General Purpose v1", "database_server_hostname": "WordPress-Database", "kitchen": "https://github.com/rackspace-orchestration-templates/wordpress-multi"}, "resource_registry": {"resources": {}, "https://raw.githubusercontent.com/rackspace-orchestration-templates/wordpress-multi/master/wordpress-web-server.yaml": "https://raw.githubusercontent.com/rackspace-orchestration-templates/wordpress-multi/master/wordpress-web-server.yaml"}}, "template": {"parameter_groups": [{"parameters": ["image"], "label": "Server Settings"}, {"parameters": ["wp_master_server_flavor", "wp_web_server_count", "wp_web_server_flavor"], "label": "Web Server Settings"}, {"parameters": ["database_server_flavor"], "label": "Database Settings"}, {"parameters": ["domain", "username"], "label": "WordPress Settings"}, {"parameters": ["kitchen", "chef_version", "child_template", "version", "prefix", "load_balancer_hostname", "wp_web_server_hostnames", "wp_master_server_hostname", "database_server_hostname"], "label": "rax-dev-params"}], "heat_template_version": "2013-05-23", "description": "This is a Heat template to deploy Load Balanced WordPress servers with a\\nbackend database server.\\n", "parameters": {"username": {"default": "wp_user", "label": "Username", "type": "string", "description": "Username for system, database, and WordPress logins.", "constraints": [{"allowed_pattern": "^[a-zA-Z0-9 _.@-]{1,16}$", "description": "Must be shorter than 16 characters and may only contain alphanumeric\\ncharacters, \' \', \'_\', \'.\', \'@\', and/or \'-\'.\\n"}]}, "domain": {"default": "example.com", "label": "Site Domain", "type": "string", "description": "Domain to be used with this WordPress site", "constraints": [{"allowed_pattern": "^[a-zA-Z0-9.-]{1,255}.[a-zA-Z]{2,15}$", "description": "Must be a valid domain name"}]}, "chef_version": {"default": "11.16.2", "type": "string", "description": "Version of chef client to use", "label": "Chef Version"}, "wp_web_server_flavor": {"default": "2 GB General Purpose v1", "label": "Node Server Size", "type": "string", "description": "Cloud Server size to use on all of the additional web nodes.\\n", "constraints": [{"description": "Must be a valid Rackspace Cloud Server flavor for the region you have\\nselected to deploy into.\\n", "allowed_values": ["1 GB General Purpose v1", "2 GB General Purpose v1", "4 GB General Purpose v1", "8 GB General Purpose v1", "15 GB I/O v1", "30 GB I/O v1", "1GB Standard Instance", "2GB Standard Instance", "4GB Standard Instance", "8GB Standard Instance", "15GB Standard Instance", "30GB Standard Instance"]}]}, "wp_web_server_hostnames": {"default": "WordPress-Web%index%", "label": "Server Name", "type": "string", "description": "Hostname to use for all additional WordPress web nodes", "constraints": [{"length": {"max": 64, "min": 1}}, {"allowed_pattern": "^[a-zA-Z][a-zA-Z0-9%-]*$", "description": "Must begin with a letter and contain only alphanumeric characters.\\n"}]}, "image": {"default": "Ubuntu 12.04 LTS (Precise Pangolin) (PVHVM)", "label": "Operating System", "type": "string", "description": "Required: Server image used for all servers that are created as a part of\\nthis deployment.\\n", "constraints": [{"description": "Must be a supported operating system.", "allowed_values": ["Ubuntu 12.04 LTS (Precise Pangolin) (PVHVM)"]}]}, "load_balancer_hostname": {"default": "WordPress-Load-Balancer", "label": "Load Balancer Hostname", "type": "string", "description": "Hostname for the Cloud Load Balancer", "constraints": [{"length": {"max": 64, "min": 1}}, {"allowed_pattern": "^[a-zA-Z][a-zA-Z0-9-]*$", "description": "Must begin with a letter and contain only alphanumeric characters.\\n"}]}, "child_template": {"default": "https://raw.githubusercontent.com/rackspace-orchestration-templates/wordpress-multi/master/wordpress-web-server.yaml", "type": "string", "description": "Location of the child template to use for the WordPress web servers\\n", "label": "Child Template"}, "wp_master_server_hostname": {"default": "WordPress-Master", "label": "Server Name", "type": "string", "description": "Hostname to use for your WordPress web-master server.", "constraints": [{"length": {"max": 64, "min": 1}}, {"allowed_pattern": "^[a-zA-Z][a-zA-Z0-9-]*$", "description": "Must begin with a letter and contain only alphanumeric characters.\\n"}]}, "prefix": {"default": "wp_", "label": "Wordpress Prefix", "type": "string", "description": "Prefix to use for database table names.", "constraints": [{"allowed_pattern": "^[0-9a-zA-Z$_]{0,10}$", "description": "Prefix must be shorter than 10 characters, and can only include\\nletters, numbers, $, and/or underscores.\\n"}]}, "version": {"default": "3.9.2", "label": "WordPress Version", "type": "string", "description": "Version of WordPress to install", "constraints": [{"allowed_values": ["3.9.2"]}]}, "wp_master_server_flavor": {"default": "2 GB General Purpose v1", "label": "Master Server Size", "type": "string", "description": "Cloud Server size to use for the web-master node. The size should be at\\nleast one size larger than what you use for the web nodes. This server\\nhandles all admin calls and will ensure files are synced across all\\nother nodes.\\n", "constraints": [{"description": "Must be a valid Rackspace Cloud Server flavor for the region you have\\nselected to deploy into.\\n", "allowed_values": ["1 GB General Purpose v1", "2 GB General Purpose v1", "4 GB General Purpose v1", "8 GB General Purpose v1", "15 GB I/O v1", "30 GB I/O v1", "1GB Standard Instance", "2GB Standard Instance", "4GB Standard Instance", "8GB Standard Instance", "15GB Standard Instance", "30GB Standard Instance"]}]}, "database_name": {"default": "wordpress", "label": "Database Name", "type": "string", "description": "WordPress database name", "constraints": [{"allowed_pattern": "^[0-9a-zA-Z$_]{1,64}$", "description": "Maximum length of 64 characters, may only contain letters, numbers, and\\nunderscores.\\n"}]}, "wp_web_server_count": {"default": 1, "label": "Web Server Count", "type": "number", "description": "Number of web servers to deploy in addition to the web-master", "constraints": [{"range": {"max": 7, "min": 0}, "description": "Must be between 0 and 7 servers."}]}, "database_server_flavor": {"default": "4 GB General Purpose v1", "label": "Server Size", "type": "string", "description": "Cloud Server size to use for the database server. Sizes refer to the\\namount of RAM allocated to the server.\\n", "constraints": [{"description": "Must be a valid Rackspace Cloud Server flavor for the region you have\\nselected to deploy into.\\n", "allowed_values": ["2 GB General Purpose v1", "4 GB General Purpose v1", "8 GB General Purpose v1", "15 GB I/O v1", "30 GB I/O v1", "2GB Standard Instance", "4GB Standard Instance", "8GB Standard Instance", "15GB Standard Instance", "30GB Standard Instance"]}]}, "database_server_hostname": {"default": "WordPress-Database", "label": "Server Name", "type": "string", "description": "Hostname to use for your WordPress Database Server", "constraints": [{"length": {"max": 64, "min": 1}}, {"allowed_pattern": "^[a-zA-Z][a-zA-Z0-9-]*$", "description": "Must begin with a letter and contain only alphanumeric characters.\\n"}]}, "kitchen": {"default": "https://github.com/rackspace-orchestration-templates/wordpress-multi", "type": "string", "description": "URL for the kitchen to use, fetched using git\\n", "label": "Kitchen"}}, "outputs": {"private_key": {"description": "SSH Private IP", "value": {"get_attr": ["ssh_key", "private_key"]}}, "load_balancer_ip": {"description": "Load Balancer IP", "value": {"get_attr": ["load_balancer", "PublicIp"]}}, "mysql_root_password": {"description": "MySQL Root Password", "value": {"get_attr": ["mysql_root_password", "value"]}}, "wordpress_user": {"description": "WordPress User", "value": {"get_param": "username"}}, "wordpress_web_ips": {"description": "Web Server IPs", "value": {"get_attr": ["wp_web_servers", "accessIPv4"]}}, "wordpress_password": {"description": "WordPress Password", "value": {"get_attr": ["database_password", "value"]}}, "database_server_ip": {"description": "Database Server IP", "value": {"get_attr": ["database_server", "accessIPv4"]}}, "wordpress_web_master_ip": {"description": "Web-Master IP", "value": {"get_attr": ["wp_master_server", "accessIPv4"]}}}, "resources": {"load_balancer": {"depends_on": ["wp_master_server_setup", "wp_web_servers"], "type": "Rackspace::Cloud::LoadBalancer", "properties": {"protocol": "HTTP", "name": {"get_param": "load_balancer_hostname"}, "algorithm": "ROUND_ROBIN", "virtualIps": [{"ipVersion": "IPV4", "type": "PUBLIC"}], "contentCaching": "ENABLED", "healthMonitor": {"attemptsBeforeDeactivation": 2, "statusRegex": "^[23]0[0-2]$", "delay": 10, "timeout": 5, "path": "/", "type": "HTTP"}, "nodes": [{"addresses": [{"get_attr": ["wp_master_server", "privateIPv4"]}], "condition": "ENABLED", "port": 80}, {"addresses": {"get_attr": ["wp_web_servers", "privateIPv4"]}, "condition": "ENABLED", "port": 80}], "port": 80, "metadata": {"rax-heat": {"get_param": "OS::stack_id"}}}}, "sync_key": {"type": "OS::Nova::KeyPair", "properties": {"name": {"str_replace": {"params": {"%stack_id%": {"get_param": "OS::stack_id"}}, "template": "%stack_id%-sync"}}, "save_private_key": true}}, "database_server": {"type": "Rackspace::Cloud::Server", "properties": {"key_name": {"get_resource": "ssh_key"}, "flavor": {"get_param": "database_server_flavor"}, "image": {"get_param": "image"}, "name": {"get_param": "database_server_hostname"}, "metadata": {"rax-heat": {"get_param": "OS::stack_id"}}}}, "wp_web_servers": {"depends_on": "database_server", "type": "OS::Heat::ResourceGroup", "properties": {"count": {"get_param": "wp_web_server_count"}, "resource_def": {"type": {"get_param": "child_template"}, "properties": {"domain": {"get_param": "domain"}, "image": {"get_param": "image"}, "wp_nonce": {"get_attr": ["wp_nonce", "value"]}, "memcached_host": {"get_attr": ["database_server", "privateIPv4"]}, "prefix": {"get_param": "prefix"}, "ssh_private_key": {"get_attr": ["ssh_key", "private_key"]}, "lsync_pub": {"get_attr": ["sync_key", "public_key"]}, "wp_auth": {"get_attr": ["wp_auth", "value"]}, "version": {"get_param": "version"}, "chef_version": {"get_param": "chef_version"}, "username": {"get_param": "username"}, "wp_web_server_flavor": {"get_param": "wp_web_server_flavor"}, "varnish_master_backend": {"get_attr": ["wp_master_server", "privateIPv4"]}, "parent_stack_id": {"get_param": "OS::stack_id"}, "wp_logged_in": {"get_attr": ["wp_logged_in", "value"]}, "kitchen": {"get_param": "kitchen"}, "wp_secure_auth": {"get_attr": ["wp_secure_auth", "value"]}, "ssh_keypair_name": {"get_resource": "ssh_key"}, "database_name": {"get_param": "database_name"}, "wp_web_server_hostname": {"get_param": "wp_web_server_hostnames"}, "ssh_public_key": {"get_attr": ["ssh_key", "public_key"]}, "database_password": {"get_attr": ["database_password", "value"]}, "database_host": {"get_attr": ["database_server", "privateIPv4"]}}}}}, "wp_secure_auth": {"type": "OS::Heat::RandomString", "properties": {"length": 32, "sequence": "hexdigits"}}, "mysql_root_password": {"type": "OS::Heat::RandomString", "properties": {"length": 16, "sequence": "lettersdigits"}}, "mysql_debian_password": {"type": "OS::Heat::RandomString", "properties": {"length": 16, "sequence": "lettersdigits"}}, "wp_auth": {"type": "OS::Heat::RandomString", "properties": {"length": 32, "sequence": "hexdigits"}}, "ssh_key": {"type": "OS::Nova::KeyPair", "properties": {"name": {"get_param": "OS::stack_id"}, "save_private_key": true}}, "wp_master_server": {"type": "Rackspace::Cloud::Server", "properties": {"key_name": {"get_resource": "ssh_key"}, "flavor": {"get_param": "wp_master_server_flavor"}, "image": {"get_param": "image"}, "name": {"get_param": "wp_master_server_hostname"}, "metadata": {"rax-heat": {"get_param": "OS::stack_id"}}}}, "database_server_firewall": {"depends_on": "wp_master_server_setup", "type": "OS::Heat::ChefSolo", "properties": {"node": {"run_list": ["recipe[rax-wordpress::memcached-firewall]"], "rax": {"memcached": {"clients": [{"get_attr": ["wp_master_server", "privateIPv4"]}, {"get_attr": ["wp_web_servers", "privateIPv4"]}]}}}, "username": "root", "private_key": {"get_attr": ["ssh_key", "private_key"]}, "host": {"get_attr": ["database_server", "accessIPv4"]}, "chef_version": {"get_param": "chef_version"}, "kitchen": {"get_param": "kitchen"}}}, "database_server_setup": {"depends_on": "database_server", "type": "OS::Heat::ChefSolo", "properties": {"node": {"run_list": ["recipe[apt]", "recipe[build-essential]", "recipe[rax-firewall]", "recipe[mysql::server]", "recipe[rax-wordpress::memcached-firewall]", "recipe[memcached]", "recipe[rax-wordpress::mysql]", "recipe[rax-wordpress::mysql-firewall]", "recipe[hollandbackup]", "recipe[hollandbackup::mysqldump]", "recipe[hollandbackup::main]", "recipe[hollandbackup::backupsets]", "recipe[hollandbackup::cron]"], "memcached": {"memory": 500, "listen": {"get_attr": ["database_server", "privateIPv4"]}}, "hollandbackup": {"main": {"mysqldump": {"host": "localhost", "password": {"get_attr": ["mysql_root_password", "value"]}, "user": "root"}, "backup_directory": "/var/lib/mysqlbackup"}}, "rax": {"firewall": {"tcp": [22]}, "mysql": {"innodb_buffer_pool_mempercent": 0.6}}, "mysql": {"remove_test_database": true, "root_network_acl": ["10.%"], "server_debian_password": {"get_attr": ["mysql_debian_password", "value"]}, "server_root_password": {"get_attr": ["mysql_root_password", "value"]}, "bind_address": {"get_attr": ["database_server", "privateIPv4"]}, "remove_anonymous_users": true, "server_repl_password": {"get_attr": ["mysql_repl_password", "value"]}}}, "username": "root", "private_key": {"get_attr": ["ssh_key", "private_key"]}, "host": {"get_attr": ["database_server", "accessIPv4"]}, "chef_version": {"get_param": "chef_version"}, "kitchen": {"get_param": "kitchen"}}}, "wp_master_server_setup": {"depends_on": ["database_server_setup", "wp_web_servers"], "type": "OS::Heat::ChefSolo", "properties": {"node": {"varnish": {"version": "3.0", "listen_port": "80"}, "sysctl": {"values": {"fs.inotify.max_user_watches": 1000000}}, "lsyncd": {"interval": 5}, "monit": {"mail_format": {"from": "monit@localhost"}, "notify_email": "root@localhost"}, "vsftpd": {"chroot_local_user": false, "ssl_ciphers": "AES256-SHA", "write_enable": true, "local_umask": "002", "hide_ids": false, "ssl_enable": true, "ipaddress": ""}, "wordpress": {"keys": {"logged_in": {"get_attr": ["wp_logged_in", "value"]}, "secure_auth_key": {"get_attr": ["wp_secure_auth", "value"]}, "nonce_key": {"get_attr": ["wp_nonce", "value"]}, "auth": {"get_attr": ["wp_auth", "value"]}}, "server_aliases": [{"get_param": "domain"}], "version": {"get_param": "version"}, "db": {"host": {"get_attr": ["database_server", "privateIPv4"]}, "user": {"get_param": "username"}, "name": {"get_param": "database_name"}, "pass": {"get_attr": ["database_password", "value"]}}, "dir": {"str_replace": {"params": {"%domain%": {"get_param": "domain"}}, "template": "/var/www/vhosts/%domain%"}}}, "run_list": ["recipe[apt]", "recipe[build-essential]", "recipe[mysql::client]", "recipe[mysql-chef_gem]", "recipe[rax-wordpress::apache-prep]", "recipe[sysctl::attribute_driver]", "recipe[rax-wordpress::x509]", "recipe[php]", "recipe[rax-install-packages]", "recipe[rax-wordpress::wp-database]", "recipe[wordpress]", "recipe[rax-wordpress::wp-setup]", "recipe[rax-wordpress::user]", "recipe[rax-wordpress::memcache]", "recipe[lsyncd]", "recipe[vsftpd]", "recipe[rax-wordpress::vsftpd]", "recipe[varnish::repo]", "recipe[varnish]", "recipe[rax-wordpress::apache]", "recipe[rax-wordpress::varnish]", "recipe[rax-wordpress::varnish-firewall]", "recipe[rax-wordpress::firewall]", "recipe[rax-wordpress::vsftpd-firewall]", "recipe[rax-wordpress::lsyncd]"], "mysql": {"server_root_password": {"get_attr": ["mysql_root_password", "value"]}, "bind_address": {"get_attr": ["mysql_root_password", "value"]}}, "apache": {"listen_ports": [8080], "serversignature": "Off", "traceenable": "Off", "timeout": 30}, "rax": {"varnish": {"master_backend": "localhost"}, "lsyncd": {"clients": {"get_attr": ["wp_web_servers", "privateIPv4"]}, "ssh": {"private_key": {"get_attr": ["sync_key", "private_key"]}}}, "memcache": {"server": {"get_attr": ["database_server", "privateIPv4"]}}, "wordpress": {"admin_pass": {"get_attr": ["database_password", "value"]}, "admin_user": {"get_param": "username"}, "user": {"group": {"get_param": "username"}, "name": {"get_param": "username"}}}, "apache": {"domain": {"get_param": "domain"}}, "packages": ["php5-imagick"]}}, "username": "root", "private_key": {"get_attr": ["ssh_key", "private_key"]}, "host": {"get_attr": ["wp_master_server", "accessIPv4"]}, "chef_version": {"get_param": "chef_version"}, "kitchen": {"get_param": "kitchen"}}}, "wp_logged_in": {"type": "OS::Heat::RandomString", "properties": {"length": 32, "sequence": "hexdigits"}}, "mysql_repl_password": {"type": "OS::Heat::RandomString", "properties": {"length": 16, "sequence": "lettersdigits"}}, "database_password": {"type": "OS::Heat::RandomString", "properties": {"length": 16, "sequence": "lettersdigits"}}, "wp_nonce": {"type": "OS::Heat::RandomString", "properties": {"length": 32, "sequence": "hexdigits"}}}}, "action": "CREATE", "project_id": "897502", "id": "5cdde045-9767-46de-ab03-a8066725d5d4", "resources": {"load_balancer": {"status": "COMPLETE", "name": "load_balancer", "resource_data": {}, "resource_id": "75917", "action": "CREATE", "type": "Rackspace::Cloud::LoadBalancer", "metadata": {}}, "sync_key": {"status": "COMPLETE", "name": "sync_key", "resource_data": {"private_key": "-----BEGIN RSA PRIVATE KEY-----\\nMIIEpAIBAAKCAQEA01UNQNUXRMmXVIHQcIc+7Vop/Jzq2Tr4WD+YNjd24D2/2uzw\\nUy5/FWgqyhnxD2+QCUX2oAJBWBNENjaUxN6AuhWu7/iE4+qklVsOctaXh2kQwM8M\\n4dg6NSQXGosqgfb3uN5uLp7UBO7qj21STP0yn1l33O5Z8CNAfQl3GjYEWfZk4QAh\\nAbzalyjezmTUyHyyBt7rNBtkIP7Ck+kXI/AwPZc8P2t0aTFkAqzdH5yJl3ZiuOHV\\nRyxVXSLUxa7LvZ7dSCFdUUxfSwJnIIEz7Kw2wglSFLmWnc5/b1dW/htHPGFkdR7h\\nJTOkcKecJDRebfL8k5at5ezaww7GBDRZtG9LhwIDAQABAoIBAQDEs72KQs1NsXWx\\nqsKgesIPmoTKJCRT3ZeaTFcY37c+MTuKQk/OnNCc1EA/rLW7cFPYzc4oUPERUZ2D\\n+HmwZIncqqIRqnfGzHg0rHReX27bEugNDqsm62QCYn0+r5n5Li6VXDOiISOnE9ov\\ndcnM7z9XIqd2dEQySB2WRGEffHfAYu2Wjm8s7cGm5iOJPsFH2lWu8dU6wUZzoSRI\\nOZFSEHiI3KKWdUNGXZT6O2LmNZqLcNsnZcH16ZwT/Ki3IMKJRM+iQ0k7v2vPtz+t\\nenQ0cHEPIhMwrFoyZtJWMFBdOICwvLFWYWvkrxAfBZJ1o5YREBwgVaEb7Eg2IUer\\nBPMYjDyBAoGBAO4DfnCGnvQqKVOYMrCJ5MZq66kUkRK1hvZXQlbHEZU+mtwPUpYH\\nKe5JKrGEPQ7eUZt16itEA6xtYmL7J1idCdZmFpg79xNI/oDUXPacK1Lp/WY+PlUf\\nfjQQ0yV+prE1LYnApn0EL5871aZD5IlhV7+m+EVRof9u8EmrLGpo7jn/AoGBAONN\\nZB7S5DnwEjNaCwR9U+Bsepw3SIIl+NJ51PFDtxyeZ+5+fhYZo/d88JtEPzY6dJ9o\\nkPTMnrsCYdBaQJGJXl1wprSRsAx00x6Ur38XEqTtsEFOG1LSnPT/Fq6JdO44olY+\\nWJ7ssgNVkHOp5Z9yLLmU80bl9Gum8HcgNG2K9h55AoGAH/32O9fMe9NC9MqLXbFb\\nP9RVUsfB7DrcJjZ6Y0GkumPM2vFwT1wtJatOAshckKgPXg8OZ7xfpgiZ5eYOVtnc\\n3aWhOdstjbkNBHIHANri8+Uhu2F4bWarRwJP70VD0KPuOAreFgW/BO88+3k6ucCM\\n0+T0kBS16qiVwcExWig6hS8CgYBg1446m7tk++WlP03GYeckjNNITz1zRd5XPlT9\\nXc5cQRkiwX3SyKXVQcP5QwBziEA70n8/7RYLsx4dePZdi1tLED3WXOPWysdQFiUX\\nTqtA3YvkpvR5OwZoU25Eeof5HuP7PqDfRRUq2n+q583POwPXJaDoqfyTCRMWjgAI\\nU9Y8cQKBgQCz+r6kPrK/7m5h+amTCDPYexW103Dl5vOHyHI9NZjd8TmMVLB8Ciqp\\nwjHPiagtovuaewN/blJ5TBzTsTlbPCq2C6yyx91kCqSdbwdRwmYCmHn9zXynBtfq\\n/SwgrxYvi9kihyU+4tKMIOvJiOTj4sK+g75oLlcbTyXjtYiGkGBmkg==\\n-----END RSA PRIVATE KEY-----\\n"}, "resource_id": "5cdde045-9767-46de-ab03-a8066725d5d4-sync", "action": "CREATE", "type": "OS::Nova::KeyPair", "metadata": {}}, "database_server": {"status": "COMPLETE", "name": "database_server", "resource_data": {"private_key": "-----BEGIN RSA PRIVATE KEY-----\\nMIICXQIBAAKBgQDzp2UCIsm7nkO99JJBgLfPe+smZx76C9NPkDYzaLnds5Cwh6nx\\n9xi2Pu5EMq53+rycUO7BDgTRXoUrbLY28uM6h8gMdmjbGPlzKiM5h9s+4RWB51YS\\nLkCg9fWXeE+xszG7tbUzXM9zrU36x8IUD+c9kEYioNQ16qBEa4dawJP7GwIDAQAB\\nAoGBAOckujIYhoAyV9lwlv8E+VsgF6hK05wqc8Ba8tA6XXjwzCZrzND6tLrPYIHa\\nAqFXgG5aaOVEQ1XL8VGMxB/Es8INCAumhKaejVoKwURLM5rpkQsqSr+9DkuAIHT+\\nqEek5oNbf1HXS4ERjchcNLmT77LP1yJjctkFcmlEvfH5oy1BAkEA+K4xbJ+iMd/u\\n5/oQF7jrRLzqdgdqTEneZLwPt1ZwruJWO1jrWcs1encSIlSGDD16uKl0uBdMe52K\\nevIoXZg02QJBAPrTU47uiiNhsAlS+/YSdPViqyCkxXbhl92uQGyKexY0YkIJepkj\\nmebREgMCLTb/CKEeq9stfD/5MfrUpW8zJxMCQDRgI8K4AGY2vs+W6ErGxK5uh4ci\\nWq4EpNVckobPqt36h6TqPm9kEDhh2aznVnA/hphcAFxBc/dZH/BzDjNgOkkCQQCV\\nhMILsyC/hK0mccRm5Iu5925hkDdx7XrVF9mpmkdTbjigevwNK87DbB/bkUGYxiDD\\nwv/ZMN0fWZI0nuxbRFfnAkBe+T2qRAidQl4PJFxnWr/oS0Z/UPpSuDDy+lnMRha2\\nXXrIirE/bM5IsYfYfEsfTLvpwMpl9my8VZ/JEkIuu/O1\\n-----END RSA PRIVATE KEY-----"}, "resource_id": "dfe4a396-bb40-4779-9562-c6ecbc6f9e2c", "action": "CREATE", "type": "Rackspace::Cloud::Server", "metadata": {}}, "wp_web_servers": {"status": "COMPLETE", "name": "ADOPT_98324-wp_web_servers-nmyzh5ebxqjk", "stack_user_project_id": "897502", "environment": {"parameter_defaults": {}, "parameters": {}, "resource_registry": {"resources": {}, "https://raw.githubusercontent.com/rackspace-orchestration-templates/wordpress-multi/master/wordpress-web-server.yaml": "https://raw.githubusercontent.com/rackspace-orchestration-templates/wordpress-multi/master/wordpress-web-server.yaml"}}, "template": {"heat_template_version": "2013-05-23", "resources": {"0": {"type": "https://raw.githubusercontent.com/rackspace-orchestration-templates/wordpress-multi/master/wordpress-web-server.yaml", "properties": {"domain": "example.com", "image": "Ubuntu 12.04 LTS (Precise Pangolin) (PVHVM)", "wp_nonce": "E6E16A60BCE928B173C2E68BCAD8DA46", "memcached_host": "10.176.197.160", "prefix": "wp_", "ssh_private_key": "-----BEGIN RSA PRIVATE KEY-----\\nMIIEowIBAAKCAQEA1Kx41PKBXtyr15H9L0c5wYc9e9ZOcoQU101CHkeAH/Aj+Ucr\\nNZbRWubL8yhLosbNqlJq4PfWZoO4Rg6xBPcHmuu8Ty7TgYLHjxbdfbBcN/Ji9kAg\\nxRhgLYIoj46yY/9NYuQVuBYXe2hYnKZlWag2/XWomuDPtjM/L2ZvVmd8kIsxUinl\\nw+O37EXtWXc3YVoyakxtULSRjQ0fcNW3haSXmmUd+lWj6tVXporcx003rmd7ZyVg\\nCDyYhy7cxlZBQNo4JWIZvnKn5RxHUCAVTtOdTNF+eFfUxdMPvnBlJUbjZwyjVAFF\\nVXrZKUqnBfnrRo6/aua+zvwhUszmHlBRI2EBGQIDAQABAoIBADY2aO7Pio7l7aAc\\nBNBCdcSRdujUblbeuHlRpmMVkuGRU3o93BPjCCcF4kNvqCgsSUz7iWcjhjHHrfed\\n0x4S4otpQC1nIF9JORmOmJNrm3ZfgT6IhlH3rryrCy/dDjhTYiStQ6QTbZT1unDk\\nMb2zFaFylrI0UH5/fcHVeNgrtSMbAPvsSmldvh65d45jtxRf1/wo0WBnNHF7rypc\\nw6d6uFFxd5wiGSkMjir4A7k2Coiyq+LCjZHtRBXrNqFzPsWw4g7KBrQ9Af463JpR\\nk10Z9GoI9p/UxRJQ4pQthtemDU6EUQRh4EYG1WcxlkCz2URXpWuy7mFObLqAU7iD\\ngGm+IiECgYEA/DBOKvew6D1+JA+AOAnlk0k3jEX40tHVU9aoEuh2yyQ5fel+3snI\\nDaFmhGvnGyVePAuPQ/ADaWcWpqFM0AEdB66PLKs8VBNQ0hw2indojebZlEnKV6Ur\\nc4Wk7bSBkGOWsFy2Cs1xN+VN9b02KPUvOgoOi2Rm/Y0jJQUvZqai5xUCgYEA1+NJ\\ncXaJLyx5DFFNAMAC4fDr+La/9iG7glKtqHjLXIinfKyAwLqZ4ctt+xunwz9PXERo\\n9e5QsM7jlL5uLYivjhEx6TWacycyXCVCjE1cYyiXNhV9/3SZb/NIxO4ysPCeQga6\\nAooipa2s/IUT5zb4s6K7TINdPOOW9r/VS0Do8vUCgYEAoRoStWwpvRKbZFnqpOHd\\noKtjKt8AR1z4lGhKUlnimX74ozDodVYd0GdM4Ec2CadjfaQ8zz+iTlEmrSfZs/8i\\nFmgy2mxBS8xTEwYm6WnChvP0BsDk2/yNt2ymoZtwMVcNSnjPajM3omd/1/4ZfSy0\\nELWf+PgYutzQmLOpRkApTMkCgYBRo3qvdILWGvw/gzMaWIH+jQu/BuS6n/D3jGpt\\nLhjBClBD3jvmJepxL2uMrN2ZAQTywE/syE0tP19ibUze3TR+BdSY+xNH/oeVvuVW\\nhx6rxLrB0gjOpHotkpNvHSCANs2x7DdFJJWLj4y+BVkMc4ZC8APiID8O+oWpE8wF\\n5CrzTQKBgC+wDsFVXfQCQJ/38uZ+bwwr4Iv0KtT4qynuhb8v3wPVXoVztNBk7elS\\nTBEl85CYSm4/g1TNQhXHjRu2qZIya5AL+m9anPT/JXLkLX7LH17ba6KR3AcDrMNB\\n6YldSOrsEn+utd5Ahwh3aM/34nuYVMiBJT05zeEL3U/KZBGM+eSb\\n-----END RSA PRIVATE KEY-----\\n", "lsync_pub": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDTVQ1A1RdEyZdUgdBwhz7tWin8nOrZOvhYP5g2N3bgPb/a7PBTLn8VaCrKGfEPb5AJRfagAkFYE0Q2NpTE3oC6Fa7v+ITj6qSVWw5y1peHaRDAzwzh2Do1JBcaiyqB9ve43m4untQE7uqPbVJM/TKfWXfc7lnwI0B9CXcaNgRZ9mThACEBvNqXKN7OZNTIfLIG3us0G2Qg/sKT6Rcj8DA9lzw/a3RpMWQCrN0fnImXdmK44dVHLFVdItTFrsu9nt1IIV1RTF9LAmcggTPsrDbCCVIUuZadzn9vV1b+G0c8YWR1HuElM6Rwp5wkNF5t8vyTlq3l7NrDDsYENFm0b0uH Generated-by-Nova\\n", "wp_auth": "505462F3CC71C01DD587B165FD86783E", "version": "3.9.2", "chef_version": "11.16.2", "username": "wp_user", "wp_web_server_flavor": "2 GB General Purpose v1", "varnish_master_backend": "10.176.197.145", "parent_stack_id": "5cdde045-9767-46de-ab03-a8066725d5d4", "wp_logged_in": "1B9E401F9333F0829E8776756C8FFC9F", "kitchen": "https://github.com/rackspace-orchestration-templates/wordpress-multi", "wp_secure_auth": "2216EB44D671D2731BBAB2984AFD3BEE", "ssh_keypair_name": "5cdde045-9767-46de-ab03-a8066725d5d4", "database_name": "wordpress", "wp_web_server_hostname": "WordPress-Web0", "ssh_public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDUrHjU8oFe3KvXkf0vRznBhz171k5yhBTXTUIeR4Af8CP5Rys1ltFa5svzKEuixs2qUmrg99Zmg7hGDrEE9wea67xPLtOBgsePFt19sFw38mL2QCDFGGAtgiiPjrJj/01i5BW4Fhd7aFicpmVZqDb9daia4M+2Mz8vZm9WZ3yQizFSKeXD47fsRe1ZdzdhWjJqTG1QtJGNDR9w1beFpJeaZR36VaPq1VemitzHTTeuZ3tnJWAIPJiHLtzGVkFA2jglYhm+cqflHEdQIBVO051M0X54V9TF0w++cGUlRuNnDKNUAUVVetkpSqcF+etGjr9q5r7O/CFSzOYeUFEjYQEZ Generated-by-Nova\\n", "database_password": "b5tlz5ZfgnqItOZw", "database_host": "10.176.197.160"}}}}, "action": "CREATE", "project_id": "897502", "id": "22d99b64-0887-4ac6-b064-e6cd73129606", "resources": {"0": {"status": "COMPLETE", "name": "ADOPT_98324-wp_web_servers-nmyzh5ebxqjk-0-hguo7gb3olzk", "stack_user_project_id": "897502", "environment": {"parameter_defaults": {}, "parameters": {"domain": "example.com", "image": "Ubuntu 12.04 LTS (Precise Pangolin) (PVHVM)", "wp_auth": "505462F3CC71C01DD587B165FD86783E", "parent_stack_id": "5cdde045-9767-46de-ab03-a8066725d5d4", "prefix": "wp_", "ssh_private_key": "-----BEGIN RSA PRIVATE KEY-----\\nMIIEowIBAAKCAQEA1Kx41PKBXtyr15H9L0c5wYc9e9ZOcoQU101CHkeAH/Aj+Ucr\\nNZbRWubL8yhLosbNqlJq4PfWZoO4Rg6xBPcHmuu8Ty7TgYLHjxbdfbBcN/Ji9kAg\\nxRhgLYIoj46yY/9NYuQVuBYXe2hYnKZlWag2/XWomuDPtjM/L2ZvVmd8kIsxUinl\\nw+O37EXtWXc3YVoyakxtULSRjQ0fcNW3haSXmmUd+lWj6tVXporcx003rmd7ZyVg\\nCDyYhy7cxlZBQNo4JWIZvnKn5RxHUCAVTtOdTNF+eFfUxdMPvnBlJUbjZwyjVAFF\\nVXrZKUqnBfnrRo6/aua+zvwhUszmHlBRI2EBGQIDAQABAoIBADY2aO7Pio7l7aAc\\nBNBCdcSRdujUblbeuHlRpmMVkuGRU3o93BPjCCcF4kNvqCgsSUz7iWcjhjHHrfed\\n0x4S4otpQC1nIF9JORmOmJNrm3ZfgT6IhlH3rryrCy/dDjhTYiStQ6QTbZT1unDk\\nMb2zFaFylrI0UH5/fcHVeNgrtSMbAPvsSmldvh65d45jtxRf1/wo0WBnNHF7rypc\\nw6d6uFFxd5wiGSkMjir4A7k2Coiyq+LCjZHtRBXrNqFzPsWw4g7KBrQ9Af463JpR\\nk10Z9GoI9p/UxRJQ4pQthtemDU6EUQRh4EYG1WcxlkCz2URXpWuy7mFObLqAU7iD\\ngGm+IiECgYEA/DBOKvew6D1+JA+AOAnlk0k3jEX40tHVU9aoEuh2yyQ5fel+3snI\\nDaFmhGvnGyVePAuPQ/ADaWcWpqFM0AEdB66PLKs8VBNQ0hw2indojebZlEnKV6Ur\\nc4Wk7bSBkGOWsFy2Cs1xN+VN9b02KPUvOgoOi2Rm/Y0jJQUvZqai5xUCgYEA1+NJ\\ncXaJLyx5DFFNAMAC4fDr+La/9iG7glKtqHjLXIinfKyAwLqZ4ctt+xunwz9PXERo\\n9e5QsM7jlL5uLYivjhEx6TWacycyXCVCjE1cYyiXNhV9/3SZb/NIxO4ysPCeQga6\\nAooipa2s/IUT5zb4s6K7TINdPOOW9r/VS0Do8vUCgYEAoRoStWwpvRKbZFnqpOHd\\noKtjKt8AR1z4lGhKUlnimX74ozDodVYd0GdM4Ec2CadjfaQ8zz+iTlEmrSfZs/8i\\nFmgy2mxBS8xTEwYm6WnChvP0BsDk2/yNt2ymoZtwMVcNSnjPajM3omd/1/4ZfSy0\\nELWf+PgYutzQmLOpRkApTMkCgYBRo3qvdILWGvw/gzMaWIH+jQu/BuS6n/D3jGpt\\nLhjBClBD3jvmJepxL2uMrN2ZAQTywE/syE0tP19ibUze3TR+BdSY+xNH/oeVvuVW\\nhx6rxLrB0gjOpHotkpNvHSCANs2x7DdFJJWLj4y+BVkMc4ZC8APiID8O+oWpE8wF\\n5CrzTQKBgC+wDsFVXfQCQJ/38uZ+bwwr4Iv0KtT4qynuhb8v3wPVXoVztNBk7elS\\nTBEl85CYSm4/g1TNQhXHjRu2qZIya5AL+m9anPT/JXLkLX7LH17ba6KR3AcDrMNB\\n6YldSOrsEn+utd5Ahwh3aM/34nuYVMiBJT05zeEL3U/KZBGM+eSb\\n-----END RSA PRIVATE KEY-----\\n", "lsync_pub": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDTVQ1A1RdEyZdUgdBwhz7tWin8nOrZOvhYP5g2N3bgPb/a7PBTLn8VaCrKGfEPb5AJRfagAkFYE0Q2NpTE3oC6Fa7v+ITj6qSVWw5y1peHaRDAzwzh2Do1JBcaiyqB9ve43m4untQE7uqPbVJM/TKfWXfc7lnwI0B9CXcaNgRZ9mThACEBvNqXKN7OZNTIfLIG3us0G2Qg/sKT6Rcj8DA9lzw/a3RpMWQCrN0fnImXdmK44dVHLFVdItTFrsu9nt1IIV1RTF9LAmcggTPsrDbCCVIUuZadzn9vV1b+G0c8YWR1HuElM6Rwp5wkNF5t8vyTlq3l7NrDDsYENFm0b0uH Generated-by-Nova\\n", "wp_nonce": "E6E16A60BCE928B173C2E68BCAD8DA46", "version": "3.9.2", "chef_version": "11.16.2", "username": "wp_user", "wp_web_server_flavor": "2 GB General Purpose v1", "varnish_master_backend": "10.176.197.145", "memcached_host": "10.176.197.160", "wp_logged_in": "1B9E401F9333F0829E8776756C8FFC9F", "kitchen": "https://github.com/rackspace-orchestration-templates/wordpress-multi", "wp_secure_auth": "2216EB44D671D2731BBAB2984AFD3BEE", "ssh_keypair_name": "5cdde045-9767-46de-ab03-a8066725d5d4", "database_name": "wordpress", "wp_web_server_hostname": "WordPress-Web0", "ssh_public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDUrHjU8oFe3KvXkf0vRznBhz171k5yhBTXTUIeR4Af8CP5Rys1ltFa5svzKEuixs2qUmrg99Zmg7hGDrEE9wea67xPLtOBgsePFt19sFw38mL2QCDFGGAtgiiPjrJj/01i5BW4Fhd7aFicpmVZqDb9daia4M+2Mz8vZm9WZ3yQizFSKeXD47fsRe1ZdzdhWjJqTG1QtJGNDR9w1beFpJeaZR36VaPq1VemitzHTTeuZ3tnJWAIPJiHLtzGVkFA2jglYhm+cqflHEdQIBVO051M0X54V9TF0w++cGUlRuNnDKNUAUVVetkpSqcF+etGjr9q5r7O/CFSzOYeUFEjYQEZ Generated-by-Nova\\n", "database_password": "b5tlz5ZfgnqItOZw", "database_host": "10.176.197.160"}, "resource_registry": {"resources": {}, "https://raw.githubusercontent.com/rackspace-orchestration-templates/wordpress-multi/master/wordpress-web-server.yaml": "https://raw.githubusercontent.com/rackspace-orchestration-templates/wordpress-multi/master/wordpress-web-server.yaml"}}, "template": {"outputs": {"accessIPv4": {"value": {"get_attr": ["wp_web_server", "accessIPv4"]}}, "privateIPv4": {"value": {"get_attr": ["wp_web_server", "privateIPv4"]}}}, "heat_template_version": "2013-05-23", "description": "This is a Heat template to deploy a single Linux server running a WordPress.\\n", "parameters": {"domain": {"default": "example.com", "type": "string", "description": "Domain to be used with WordPress site"}, "image": {"default": "Ubuntu 12.04 LTS (Precise Pangolin) (PVHVM)", "type": "string", "description": "Server Image used for all servers.", "constraints": [{"description": "Must be a supported operating system.", "allowed_values": ["Ubuntu 12.04 LTS (Precise Pangolin) (PVHVM)"]}]}, "wp_nonce": {"type": "string"}, "memcached_host": {"default": "127.0.0.1", "type": "string", "description": "IP/Host of the memcached server"}, "prefix": {"default": "wp_", "type": "string", "description": "Prefix to use for"}, "ssh_private_key": {"type": "string"}, "lsync_pub": {"type": "string", "description": "Public key for lsync configuration", "constraints": null}, "wp_auth": {"type": "string"}, "version": {"default": "3.9.1", "type": "string", "description": "Version of WordPress to install"}, "chef_version": {"default": "11.16.2", "type": "string", "description": "Version of chef client to use"}, "username": {"default": "wp_user", "type": "string", "description": "Username for system, database, and WordPress logins."}, "wp_web_server_flavor": {"default": "2 GB General Purpose v1", "type": "string", "description": "Web Cloud Server flavor", "constraints": [{"description": "Must be a valid Rackspace Cloud Server flavor for the region you have\\nselected to deploy into.\\n", "allowed_values": ["1 GB General Purpose v1", "2 GB General Purpose v1", "4 GB General Purpose v1", "8 GB General Purpose v1", "15 GB I/O v1", "30 GB I/O v1", "1GB Standard Instance", "2GB Standard Instance", "4GB Standard Instance", "8GB Standard Instance", "15GB Standard Instance", "30GB Standard Instance"]}]}, "varnish_master_backend": {"default": "localhost", "type": "string", "description": "Master backend host for admin calls in Varnish"}, "parent_stack_id": {"default": "none", "type": "string", "description": "Stack id of the parent stack"}, "wp_logged_in": {"type": "string"}, "kitchen": {"default": "https://github.com/rackspace-orchestration-templates/wordpress-multi", "type": "string", "description": "URL for the kitchen to use"}, "wp_secure_auth": {"type": "string"}, "ssh_keypair_name": {"type": "string", "description": "keypair name to register with Nova for the root SSH key"}, "database_name": {"default": "wordpress", "type": "string", "description": "WordPress database name"}, "wp_web_server_hostname": {"default": "WordPress-Web", "type": "string", "description": "WordPress Web Server Name", "constraints": [{"length": {"max": 64, "min": 1}}, {"allowed_pattern": "^[a-zA-Z][a-zA-Z0-9-]*$", "description": "Must begin with a letter and contain only alphanumeric characters.\\n"}]}, "ssh_public_key": {"type": "string"}, "database_password": {"type": "string", "description": "Password to use for database connections."}, "database_host": {"default": "127.0.0.1", "type": "string", "description": "IP/Host of the database server"}}, "resources": {"wp_web_server_setup": {"depends_on": "wp_web_server", "type": "OS::Heat::ChefSolo", "properties": {"username": "root", "node": {"apache": {"listen_ports": [8080], "serversignature": "Off", "traceenable": "Off", "timeout": 30}, "varnish": {"version": "3.0", "listen_port": "80"}, "wordpress": {"keys": {"logged_in": {"get_param": "wp_logged_in"}, "secure_auth_key": {"get_param": "wp_secure_auth"}, "nonce_key": {"get_param": "wp_nonce"}, "auth": {"get_param": "wp_auth"}}, "server_aliases": [{"get_param": "domain"}], "version": {"get_param": "version"}, "db": {"host": {"get_param": "database_host"}, "pass": {"get_param": "database_password"}, "user": {"get_param": "username"}, "name": {"get_param": "database_name"}}, "dir": {"str_replace": {"params": {"%domain%": {"get_param": "domain"}}, "template": "/var/www/vhosts/%domain%"}}}, "run_list": ["recipe[apt]", "recipe[build-essential]", "recipe[rax-wordpress::apache-prep]", "recipe[rax-wordpress::x509]", "recipe[php]", "recipe[rax-install-packages]", "recipe[wordpress]", "recipe[rax-wordpress::user]", "recipe[rax-wordpress::memcache]", "recipe[varnish::repo]", "recipe[varnish]", "recipe[rax-wordpress::apache]", "recipe[rax-wordpress::varnish]", "recipe[rax-wordpress::firewall]", "recipe[rax-wordpress::lsyncd-client]"], "rax": {"varnish": {"master_backend": {"get_param": "varnish_master_backend"}}, "lsyncd": {"ssh": {"pub": {"get_param": "lsync_pub"}}}, "memcache": {"server": {"get_param": "memcached_host"}}, "wordpress": {"admin_pass": {"get_param": "database_password"}, "user": {"group": {"get_param": "username"}, "name": {"get_param": "username"}}}, "apache": {"domain": {"get_param": "domain"}}, "packages": ["php5-imagick"]}}, "private_key": {"get_param": "ssh_private_key"}, "host": {"get_attr": ["wp_web_server", "accessIPv4"]}, "chef_version": {"get_param": "chef_version"}, "kitchen": {"get_param": "kitchen"}}}, "wp_web_server": {"type": "Rackspace::Cloud::Server", "properties": {"key_name": {"get_param": "ssh_keypair_name"}, "flavor": {"get_param": "wp_web_server_flavor"}, "name": {"get_param": "wp_web_server_hostname"}, "image": {"get_param": "image"}, "metadata": {"rax-heat": {"get_param": "parent_stack_id"}}}}}}, "action": "CREATE", "project_id": "897502", "id": "6134176b-9323-4c5f-a2b4-fcbe4247a45a", "resources": {"wp_web_server_setup": {"status": "COMPLETE", "name": "wp_web_server_setup", "resource_data": {"process_id": "10930"}, "resource_id": "7e50edd2-d9c1-4b32-95c6-7f42cc0f2fa5", "action": "CREATE", "type": "OS::Heat::ChefSolo", "metadata": {}}, "wp_web_server": {"status": "COMPLETE", "name": "wp_web_server", "resource_data": {"private_key": "-----BEGIN RSA PRIVATE KEY-----\\nMIICXAIBAAKBgQCR0v1FW8Sgn/zwFXAz5qV9ru0KgRYKtBPW9K1A50czATT8FQaE\\n9vMPVBdiINGpNqGw31QEJG7q2eiSu2fh6SxP7FYlGB9zKkOfK7RQr4qK8uthI3ee\\n4RHE7gu1/WpoRLH05EioS6ysxXwdMwU/9VYfV9pgRBWuT+095I3OFw5KNwIDAQAB\\nAoGAJpra3i/LQFLanZyvVa4sBbf3nR5LfY3q6q9f5pzT5pbdNhdC4JSYCGjUv++8\\nUbXa3H5jOa2Dh70kqyPd/prCVgfdu57vK0XdhuoxRdQRwTKnZKoDGL0AS8r2pQzJ\\nLbHKPgj46AJCCn/7sV+ruVQsK8Z/m8zoLyNI/CUzHBaPweECQQC2i2Nc6cDntC+I\\n9eNVpXyfE/mRYRWha0OAo8W68Ts01JLiQY448/XL+IiSLWm+/HpaYj+DRY8YmH/X\\nERD0FDSZAkEAzIDmjM7o3i9H3DoLari+HPGmK5pgSYViL+aJXcvbL8ut62EugaYz\\nY4p3RnABaqZA4cxBvONrvl4L5ccV0bznTwJBAJ1A3Lso37Z7IcwBzvJ0GjRMF91m\\nXiTta3xBGVBfCZsMWPCyepuThjZNhxEuL/+ILrr4EjC61nfgv5h9KjapxVkCQHY/\\nppAO6DnpLu0ZpxZboppL5GDcEAcTGFZIQG+6+4+kf3lWJTUUbCyHmTZid386iNPH\\nbs+Q1PErokeIGYbAayMCQHS+pmhUDpRD/tX9QscDjrJibUMVcdZpVzrhCKfrlyiK\\nUoXCxlUz4E0NWxRapVkecC3HkCFmuckEdRu0IDEucEI=\\n-----END RSA PRIVATE KEY-----"}, "resource_id": "6e26e3a3-eb55-4285-8cd4-79206a359ef0", "action": "CREATE", "type": "Rackspace::Cloud::Server", "metadata": {}}}}}}, "wp_secure_auth": {"status": "COMPLETE", "name": "wp_secure_auth", "resource_data": {"value": "2216EB44D671D2731BBAB2984AFD3BEE"}, "resource_id": "ADOPT_98324-wp_secure_auth-xwza4n6mmm77", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}, "mysql_root_password": {"status": "COMPLETE", "name": "mysql_root_password", "resource_data": {"value": "zeSsquuwwdxI6dr5"}, "resource_id": "ADOPT_98324-mysql_root_password-agsw3mg4eaoc", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}, "mysql_debian_password": {"status": "COMPLETE", "name": "mysql_debian_password", "resource_data": {"value": "oMeqCl3H7A951PEx"}, "resource_id": "ADOPT_98324-mysql_debian_password-u2lbz234o2zs", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}, "wp_auth": {"status": "COMPLETE", "name": "wp_auth", "resource_data": {"value": "505462F3CC71C01DD587B165FD86783E"}, "resource_id": "ADOPT_98324-wp_auth-meqrqwgii7zr", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}, "ssh_key": {"status": "COMPLETE", "name": "ssh_key", "resource_data": {"private_key": "-----BEGIN RSA PRIVATE KEY-----\\nMIIEowIBAAKCAQEA1Kx41PKBXtyr15H9L0c5wYc9e9ZOcoQU101CHkeAH/Aj+Ucr\\nNZbRWubL8yhLosbNqlJq4PfWZoO4Rg6xBPcHmuu8Ty7TgYLHjxbdfbBcN/Ji9kAg\\nxRhgLYIoj46yY/9NYuQVuBYXe2hYnKZlWag2/XWomuDPtjM/L2ZvVmd8kIsxUinl\\nw+O37EXtWXc3YVoyakxtULSRjQ0fcNW3haSXmmUd+lWj6tVXporcx003rmd7ZyVg\\nCDyYhy7cxlZBQNo4JWIZvnKn5RxHUCAVTtOdTNF+eFfUxdMPvnBlJUbjZwyjVAFF\\nVXrZKUqnBfnrRo6/aua+zvwhUszmHlBRI2EBGQIDAQABAoIBADY2aO7Pio7l7aAc\\nBNBCdcSRdujUblbeuHlRpmMVkuGRU3o93BPjCCcF4kNvqCgsSUz7iWcjhjHHrfed\\n0x4S4otpQC1nIF9JORmOmJNrm3ZfgT6IhlH3rryrCy/dDjhTYiStQ6QTbZT1unDk\\nMb2zFaFylrI0UH5/fcHVeNgrtSMbAPvsSmldvh65d45jtxRf1/wo0WBnNHF7rypc\\nw6d6uFFxd5wiGSkMjir4A7k2Coiyq+LCjZHtRBXrNqFzPsWw4g7KBrQ9Af463JpR\\nk10Z9GoI9p/UxRJQ4pQthtemDU6EUQRh4EYG1WcxlkCz2URXpWuy7mFObLqAU7iD\\ngGm+IiECgYEA/DBOKvew6D1+JA+AOAnlk0k3jEX40tHVU9aoEuh2yyQ5fel+3snI\\nDaFmhGvnGyVePAuPQ/ADaWcWpqFM0AEdB66PLKs8VBNQ0hw2indojebZlEnKV6Ur\\nc4Wk7bSBkGOWsFy2Cs1xN+VN9b02KPUvOgoOi2Rm/Y0jJQUvZqai5xUCgYEA1+NJ\\ncXaJLyx5DFFNAMAC4fDr+La/9iG7glKtqHjLXIinfKyAwLqZ4ctt+xunwz9PXERo\\n9e5QsM7jlL5uLYivjhEx6TWacycyXCVCjE1cYyiXNhV9/3SZb/NIxO4ysPCeQga6\\nAooipa2s/IUT5zb4s6K7TINdPOOW9r/VS0Do8vUCgYEAoRoStWwpvRKbZFnqpOHd\\noKtjKt8AR1z4lGhKUlnimX74ozDodVYd0GdM4Ec2CadjfaQ8zz+iTlEmrSfZs/8i\\nFmgy2mxBS8xTEwYm6WnChvP0BsDk2/yNt2ymoZtwMVcNSnjPajM3omd/1/4ZfSy0\\nELWf+PgYutzQmLOpRkApTMkCgYBRo3qvdILWGvw/gzMaWIH+jQu/BuS6n/D3jGpt\\nLhjBClBD3jvmJepxL2uMrN2ZAQTywE/syE0tP19ibUze3TR+BdSY+xNH/oeVvuVW\\nhx6rxLrB0gjOpHotkpNvHSCANs2x7DdFJJWLj4y+BVkMc4ZC8APiID8O+oWpE8wF\\n5CrzTQKBgC+wDsFVXfQCQJ/38uZ+bwwr4Iv0KtT4qynuhb8v3wPVXoVztNBk7elS\\nTBEl85CYSm4/g1TNQhXHjRu2qZIya5AL+m9anPT/JXLkLX7LH17ba6KR3AcDrMNB\\n6YldSOrsEn+utd5Ahwh3aM/34nuYVMiBJT05zeEL3U/KZBGM+eSb\\n-----END RSA PRIVATE KEY-----\\n"}, "resource_id": "5cdde045-9767-46de-ab03-a8066725d5d4", "action": "CREATE", "type": "OS::Nova::KeyPair", "metadata": {}}, "wp_master_server": {"status": "COMPLETE", "name": "wp_master_server", "resource_data": {"private_key": "-----BEGIN RSA PRIVATE KEY-----\\nMIICXAIBAAKBgQCx492mKsc0PRigaaLQ/oVspyepbXAEbC9hkNnBxOtEgeVqHiWu\\nmzpJfHeVk+fX/ud5/HkJexED1FL1zfUkAjajgis9n8/AaznAHv+3qI2VSuMJzmKX\\n2fHqBdhp6CsdAkNd68TcBgcyruZHkq8K9slp58BeKsxKpvlq0tZHwXavpwIDAQAB\\nAoGAIzMboM3GLSgJv3Qnq4Mxk5Zf2r6086sUlRG8hQMaKqwpYR4mBq7gkbn3T7m8\\nnpjp5NF4gc/ARim1YL4oS7/EX7E3NC/UwO6zSnitlIYzE/yBDNNEHvdIeqhZt1fP\\nhXAGyvot7n1rWp+79cOCOqr2ZgzdAHkBrQE7Tb+6TSzUfUECQQC77xwnAvcjSEcC\\nZORCpnw8nvuaRspfXiCSbkVosZxIEJUUUnn0tSccnGkra/Q+5k1GF3nn+K+VkM5a\\nGo4ZG5krAkEA8lGAkCeUTqaXq9f/s3PtAJWtd4ZcBRck39MDJSmlYBiq0PQvn2sn\\nnxvNrG8vuetN1yMFn3zI96kQzdrl5PeNdQJBAKrHr/qXjEPIs5auXmte5TkldBiP\\nSen+HHVUtchc1lr6jq7IAEFquV8bl8q4sFzUZdZTERnG+LBexdZFmWmhlb8CQFnG\\nCDNf9noNDjQEGh+J20xUJ6gYhw77vBWQP6INA8/OU7qGPP563Hr9+fzgVHY0zund\\nd7/Woz3dzPP3HSTu8eECQHkQOfXZ8L3LlSNpytMqJI9thc2fruEGUT6SYQQ+FqLM\\nP9B1LNSkYUWUleSjXPpkJwzwYa6tO6pznt0X15pfQ+0=\\n-----END RSA PRIVATE KEY-----"}, "resource_id": "f03a2553-d611-48b2-9b73-a5d343dbbee6", "action": "CREATE", "type": "Rackspace::Cloud::Server", "metadata": {}}, "database_server_firewall": {"status": "COMPLETE", "name": "database_server_firewall", "resource_data": {"process_id": "13813"}, "resource_id": "6f0a9129-cc02-45f5-8490-591e2a5982e1", "action": "CREATE", "type": "OS::Heat::ChefSolo", "metadata": {}}, "database_server_setup": {"status": "COMPLETE", "name": "database_server_setup", "resource_data": {"process_id": "10799"}, "resource_id": "b1b8d413-12e2-4bcd-ad39-8aad772e94e5", "action": "CREATE", "type": "OS::Heat::ChefSolo", "metadata": {}}, "wp_master_server_setup": {"status": "COMPLETE", "name": "wp_master_server_setup", "resource_data": {"process_id": "11131"}, "resource_id": "dba3d1a5-3e7c-469a-8845-fdc54cd6cfcb", "action": "CREATE", "type": "OS::Heat::ChefSolo", "metadata": {}}, "wp_logged_in": {"status": "COMPLETE", "name": "wp_logged_in", "resource_data": {"value": "1B9E401F9333F0829E8776756C8FFC9F"}, "resource_id": "ADOPT_98324-wp_logged_in-b24qsyi3uunc", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}, "mysql_repl_password": {"status": "COMPLETE", "name": "mysql_repl_password", "resource_data": {"value": "ev9saFHsIOGouxeN"}, "resource_id": "ADOPT_98324-mysql_repl_password-pkstv4hpfg3u", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}, "database_password": {"status": "COMPLETE", "name": "database_password", "resource_data": {"value": "b5tlz5ZfgnqItOZw"}, "resource_id": "ADOPT_98324-database_password-roujzxbp3i77", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}, "wp_nonce": {"status": "COMPLETE", "name": "wp_nonce", "resource_data": {"value": "E6E16A60BCE928B173C2E68BCAD8DA46"}, "resource_id": "ADOPT_98324-wp_nonce-gpwap4n7dkzq", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}}}
"""

adopt_data5 = """
{\n  \"status\": \"COMPLETE\", \n  \"name\": \"wordpress1\", \n  \"stack_user_project_id\": \"897686\", \n  \"environment\": {\n    \"parameter_defaults\": {}, \n    \"parameters\": {}, \n    \"resource_registry\": {\n      \"https://raw.githubusercontent.com/rackspace-orchestration-templates/wordpress-multi/master/wordpress-web-server.yaml\": \"https://raw.githubusercontent.com/rackspace-orchestration-templates/wordpress-multi/master/wordpress-web-server.yaml\", \n      \"resources\": {}\n    }\n  }, \n  \"template\": {\n    \"parameter_groups\": [\n      {\n        \"parameters\": [\n          \"image\"\n        ], \n        \"label\": \"Server Settings\"\n      }, \n      {\n        \"parameters\": [\n          \"wp_master_server_flavor\", \n          \"wp_web_server_count\", \n          \"wp_web_server_flavor\"\n        ], \n        \"label\": \"Web Server Settings\"\n      }, \n      {\n        \"parameters\": [\n          \"database_server_flavor\"\n        ], \n        \"label\": \"Database Settings\"\n      }, \n      {\n        \"parameters\": [\n          \"domain\", \n          \"username\"\n        ], \n        \"label\": \"WordPress Settings\"\n      }, \n      {\n        \"parameters\": [\n          \"kitchen\", \n          \"chef_version\", \n          \"child_template\", \n          \"version\", \n          \"prefix\", \n          \"load_balancer_hostname\", \n          \"wp_web_server_hostnames\", \n          \"wp_master_server_hostname\", \n          \"database_server_hostname\"\n        ], \n        \"label\": \"rax-dev-params\"\n      }\n    ], \n    \"heat_template_version\": \"2013-05-23\", \n    \"description\": \"This is a Heat template to deploy Load Balanced WordPress servers with a\\nbackend database server.\\n\", \n    \"parameters\": {\n      \"username\": {\n        \"default\": \"wp_user\", \n        \"constraints\": [\n          {\n            \"allowed_pattern\": \"^[a-zA-Z0-9 _.@-]{1,16}$\", \n            \"description\": \"Must be shorter than 16 characters and may only contain alphanumeric\\ncharacters, ' ', '_', '.', '@', and/or '-'.\\n\"\n          }\n        ], \n        \"type\": \"string\", \n        \"description\": \"Username for system, database, and WordPress logins.\", \n        \"label\": \"Username\"\n      }, \n      \"domain\": {\n        \"default\": \"example.com\", \n        \"constraints\": [\n          {\n            \"allowed_pattern\": \"^[a-zA-Z0-9.-]{1,255}.[a-zA-Z]{2,15}$\", \n            \"description\": \"Must be a valid domain name\"\n          }\n        ], \n        \"type\": \"string\", \n        \"description\": \"Domain to be used with this WordPress site\", \n        \"label\": \"Site Domain\"\n      }, \n      \"chef_version\": {\n        \"default\": \"11.16.2\", \n        \"type\": \"string\", \n        \"description\": \"Version of chef client to use\", \n        \"label\": \"Chef Version\"\n      }, \n      \"wp_web_server_flavor\": {\n        \"default\": \"2 GB General Purpose v1\", \n        \"constraints\": [\n          {\n            \"description\": \"Must be a valid Rackspace Cloud Server flavor for the region you have\\nselected to deploy into.\\n\", \n            \"allowed_values\": [\n              \"1 GB General Purpose v1\", \n              \"2 GB General Purpose v1\", \n              \"4 GB General Purpose v1\", \n              \"8 GB General Purpose v1\", \n              \"15 GB I/O v1\", \n              \"30 GB I/O v1\", \n              \"1GB Standard Instance\", \n              \"2GB Standard Instance\", \n              \"4GB Standard Instance\", \n              \"8GB Standard Instance\", \n              \"15GB Standard Instance\", \n              \"30GB Standard Instance\"\n            ]\n          }\n        ], \n        \"type\": \"string\", \n        \"description\": \"Cloud Server size to use on all of the additional web nodes.\\n\", \n        \"label\": \"Node Server Size\"\n      }, \n      \"wp_web_server_hostnames\": {\n        \"default\": \"WordPress-Web%index%\", \n        \"constraints\": [\n          {\n            \"length\": {\n              \"max\": 64, \n              \"min\": 1\n            }\n          }, \n          {\n            \"allowed_pattern\": \"^[a-zA-Z][a-zA-Z0-9%-]*$\", \n            \"description\": \"Must begin with a letter and contain only alphanumeric characters.\\n\"\n          }\n        ], \n        \"type\": \"string\", \n        \"description\": \"Hostname to use for all additional WordPress web nodes\", \n        \"label\": \"Server Name\"\n      }, \n      \"image\": {\n        \"default\": \"Ubuntu 12.04 LTS (Precise Pangolin) (PVHVM)\", \n        \"constraints\": [\n          {\n            \"description\": \"Must be a supported operating system.\", \n            \"allowed_values\": [\n              \"Ubuntu 12.04 LTS (Precise Pangolin) (PVHVM)\"\n            ]\n          }\n        ], \n        \"type\": \"string\", \n        \"description\": \"Required: Server image used for all servers that are created as a part of\\nthis deployment.\\n\", \n        \"label\": \"Operating System\"\n      }, \n      \"load_balancer_hostname\": {\n        \"default\": \"WordPress-Load-Balancer\", \n        \"constraints\": [\n          {\n            \"length\": {\n              \"max\": 64, \n              \"min\": 1\n            }\n          }, \n          {\n            \"allowed_pattern\": \"^[a-zA-Z][a-zA-Z0-9-]*$\", \n            \"description\": \"Must begin with a letter and contain only alphanumeric characters.\\n\"\n          }\n        ], \n        \"type\": \"string\", \n        \"description\": \"Hostname for the Cloud Load Balancer\", \n        \"label\": \"Load Balancer Hostname\"\n      }, \n      \"database_server_hostname\": {\n        \"default\": \"WordPress-Database\", \n        \"constraints\": [\n          {\n            \"length\": {\n              \"max\": 64, \n              \"min\": 1\n            }\n          }, \n          {\n            \"allowed_pattern\": \"^[a-zA-Z][a-zA-Z0-9-]*$\", \n            \"description\": \"Must begin with a letter and contain only alphanumeric characters.\\n\"\n          }\n        ], \n        \"type\": \"string\", \n        \"description\": \"Hostname to use for your WordPress Database Server\", \n        \"label\": \"Server Name\"\n      }, \n      \"wp_master_server_hostname\": {\n        \"default\": \"WordPress-Master\", \n        \"constraints\": [\n          {\n            \"length\": {\n              \"max\": 64, \n              \"min\": 1\n            }\n          }, \n          {\n            \"allowed_pattern\": \"^[a-zA-Z][a-zA-Z0-9-]*$\", \n            \"description\": \"Must begin with a letter and contain only alphanumeric characters.\\n\"\n          }\n        ], \n        \"type\": \"string\", \n        \"description\": \"Hostname to use for your WordPress web-master server.\", \n        \"label\": \"Server Name\"\n      }, \n      \"prefix\": {\n        \"default\": \"wp_\", \n        \"constraints\": [\n          {\n            \"allowed_pattern\": \"^[0-9a-zA-Z$_]{0,10}$\", \n            \"description\": \"Prefix must be shorter than 10 characters, and can only include\\nletters, numbers, $, and/or underscores.\\n\"\n          }\n        ], \n        \"type\": \"string\", \n        \"description\": \"Prefix to use for database table names.\", \n        \"label\": \"Wordpress Prefix\"\n      }, \n      \"version\": {\n        \"default\": \"3.9.2\", \n        \"constraints\": [\n          {\n            \"allowed_values\": [\n              \"3.9.2\"\n            ]\n          }\n        ], \n        \"type\": \"string\", \n        \"description\": \"Version of WordPress to install\", \n        \"label\": \"WordPress Version\"\n      }, \n      \"wp_master_server_flavor\": {\n        \"default\": \"2 GB General Purpose v1\", \n        \"constraints\": [\n          {\n            \"description\": \"Must be a valid Rackspace Cloud Server flavor for the region you have\\nselected to deploy into.\\n\", \n            \"allowed_values\": [\n              \"1 GB General Purpose v1\", \n              \"2 GB General Purpose v1\", \n              \"4 GB General Purpose v1\", \n              \"8 GB General Purpose v1\", \n              \"15 GB I/O v1\", \n              \"30 GB I/O v1\", \n              \"1GB Standard Instance\", \n              \"2GB Standard Instance\", \n              \"4GB Standard Instance\", \n              \"8GB Standard Instance\", \n              \"15GB Standard Instance\", \n              \"30GB Standard Instance\"\n            ]\n          }\n        ], \n        \"type\": \"string\", \n        \"description\": \"Cloud Server size to use for the web-master node. The size should be at\\nleast one size larger than what you use for the web nodes. This server\\nhandles all admin calls and will ensure files are synced across all\\nother nodes.\\n\", \n        \"label\": \"Master Server Size\"\n      }, \n      \"database_name\": {\n        \"default\": \"wordpress\", \n        \"constraints\": [\n          {\n            \"allowed_pattern\": \"^[0-9a-zA-Z$_]{1,64}$\", \n            \"description\": \"Maximum length of 64 characters, may only contain letters, numbers, and\\nunderscores.\\n\"\n          }\n        ], \n        \"type\": \"string\", \n        \"description\": \"WordPress database name\", \n        \"label\": \"Database Name\"\n      }, \n      \"wp_web_server_count\": {\n        \"default\": 1, \n        \"constraints\": [\n          {\n            \"range\": {\n              \"max\": 7, \n              \"min\": 0\n            }, \n            \"description\": \"Must be between 0 and 7 servers.\"\n          }\n        ], \n        \"type\": \"number\", \n        \"description\": \"Number of web servers to deploy in addition to the web-master\", \n        \"label\": \"Web Server Count\"\n      }, \n      \"database_server_flavor\": {\n        \"default\": \"4 GB General Purpose v1\", \n        \"constraints\": [\n          {\n            \"description\": \"Must be a valid Rackspace Cloud Server flavor for the region you have\\nselected to deploy into.\\n\", \n            \"allowed_values\": [\n              \"2 GB General Purpose v1\", \n              \"4 GB General Purpose v1\", \n              \"8 GB General Purpose v1\", \n              \"15 GB I/O v1\", \n              \"30 GB I/O v1\", \n              \"2GB Standard Instance\", \n              \"4GB Standard Instance\", \n              \"8GB Standard Instance\", \n              \"15GB Standard Instance\", \n              \"30GB Standard Instance\"\n            ]\n          }\n        ], \n        \"type\": \"string\", \n        \"description\": \"Cloud Server size to use for the database server. Sizes refer to the\\namount of RAM allocated to the server.\\n\", \n        \"label\": \"Server Size\"\n      }, \n      \"child_template\": {\n        \"default\": \"https://raw.githubusercontent.com/rackspace-orchestration-templates/wordpress-multi/master/wordpress-web-server.yaml\", \n        \"type\": \"string\", \n        \"description\": \"Location of the child template to use for the WordPress web servers\\n\", \n        \"label\": \"Child Template\"\n      }, \n      \"kitchen\": {\n        \"default\": \"https://github.com/rackspace-orchestration-templates/wordpress-multi\", \n        \"type\": \"string\", \n        \"description\": \"URL for the kitchen to use, fetched using git\\n\", \n        \"label\": \"Kitchen\"\n      }\n    }, \n    \"outputs\": {\n      \"private_key\": {\n        \"description\": \"SSH Private IP\", \n        \"value\": {\n          \"get_attr\": [\n            \"ssh_key\", \n            \"private_key\"\n          ]\n        }\n      }, \n      \"load_balancer_ip\": {\n        \"description\": \"Load Balancer IP\", \n        \"value\": {\n          \"get_attr\": [\n            \"load_balancer\", \n            \"PublicIp\"\n          ]\n        }\n      }, \n      \"mysql_root_password\": {\n        \"description\": \"MySQL Root Password\", \n        \"value\": {\n          \"get_attr\": [\n            \"mysql_root_password\", \n            \"value\"\n          ]\n        }\n      }, \n      \"wordpress_user\": {\n        \"description\": \"WordPress User\", \n        \"value\": {\n          \"get_param\": \"username\"\n        }\n      }, \n      \"wordpress_web_ips\": {\n        \"description\": \"Web Server IPs\", \n        \"value\": {\n          \"get_attr\": [\n            \"wp_web_servers\", \n            \"accessIPv4\"\n          ]\n        }\n      }, \n      \"wordpress_password\": {\n        \"description\": \"WordPress Password\", \n        \"value\": {\n          \"get_attr\": [\n            \"database_password\", \n            \"value\"\n          ]\n        }\n      }, \n      \"database_server_ip\": {\n        \"description\": \"Database Server IP\", \n        \"value\": {\n          \"get_attr\": [\n            \"database_server\", \n            \"accessIPv4\"\n          ]\n        }\n      }, \n      \"wordpress_web_master_ip\": {\n        \"description\": \"Web-Master IP\", \n        \"value\": {\n          \"get_attr\": [\n            \"wp_master_server\", \n            \"accessIPv4\"\n          ]\n        }\n      }\n    }, \n    \"resources\": {\n      \"load_balancer\": {\n        \"depends_on\": [\n          \"wp_master_server_setup\", \n          \"wp_web_servers\"\n        ], \n        \"type\": \"Rackspace::Cloud::LoadBalancer\", \n        \"properties\": {\n          \"protocol\": \"HTTP\", \n          \"name\": {\n            \"get_param\": \"load_balancer_hostname\"\n          }, \n          \"algorithm\": \"ROUND_ROBIN\", \n          \"virtualIps\": [\n            {\n              \"ipVersion\": \"IPV4\", \n              \"type\": \"PUBLIC\"\n            }\n          ], \n          \"contentCaching\": \"ENABLED\", \n          \"healthMonitor\": {\n            \"attemptsBeforeDeactivation\": 2, \n            \"statusRegex\": \"^[23]0[0-2]$\", \n            \"delay\": 10, \n            \"timeout\": 5, \n            \"path\": \"/\", \n            \"type\": \"HTTP\"\n          }, \n          \"nodes\": [\n            {\n              \"addresses\": [\n                {\n                  \"get_attr\": [\n                    \"wp_master_server\", \n                    \"networks\", \n                    \"private\", \n                    0\n                  ]\n                }\n              ], \n              \"condition\": \"ENABLED\", \n              \"port\": 80\n            }, \n            {\n              \"addresses\": {\n                \"get_attr\": [\n                  \"wp_web_servers\", \n                  \"privateIPv4\"\n                ]\n              }, \n              \"condition\": \"ENABLED\", \n              \"port\": 80\n            }\n          ], \n          \"port\": 80, \n          \"metadata\": {\n            \"rax-heat\": {\n              \"get_param\": \"OS::stack_id\"\n            }\n          }\n        }\n      }, \n      \"sync_key\": {\n        \"type\": \"OS::Nova::KeyPair\", \n        \"properties\": {\n          \"name\": {\n            \"str_replace\": {\n              \"params\": {\n                \"%stack_id%\": {\n                  \"get_param\": \"OS::stack_id\"\n                }\n              }, \n              \"template\": \"%stack_id%-sync\"\n            }\n          }, \n          \"save_private_key\": true\n        }\n      }, \n      \"database_server\": {\n        \"type\": \"OS::Nova::Server\", \n        \"properties\": {\n          \"key_name\": {\n            \"get_resource\": \"ssh_key\"\n          }, \n          \"flavor\": {\n            \"get_param\": \"database_server_flavor\"\n          }, \n          \"name\": {\n            \"get_param\": \"database_server_hostname\"\n          }, \n          \"image\": {\n            \"get_param\": \"image\"\n          }, \n          \"metadata\": {\n            \"rax-heat\": {\n              \"get_param\": \"OS::stack_id\"\n            }\n          }\n        }\n      }, \n      \"wp_web_servers\": {\n        \"depends_on\": \"database_server\", \n        \"type\": \"OS::Heat::ResourceGroup\", \n        \"properties\": {\n          \"count\": {\n            \"get_param\": \"wp_web_server_count\"\n          }, \n          \"resource_def\": {\n            \"type\": {\n              \"get_param\": \"child_template\"\n            }, \n            \"properties\": {\n              \"domain\": {\n                \"get_param\": \"domain\"\n              }, \n              \"image\": {\n                \"get_param\": \"image\"\n              }, \n              \"wp_nonce\": {\n                \"get_attr\": [\n                  \"wp_nonce\", \n                  \"value\"\n                ]\n              }, \n              \"memcached_host\": {\n                \"get_attr\": [\n                  \"database_server\", \n                  \"networks\", \n                  \"private\", \n                  0\n                ]\n              }, \n              \"prefix\": {\n                \"get_param\": \"prefix\"\n              }, \n              \"ssh_private_key\": {\n                \"get_attr\": [\n                  \"ssh_key\", \n                  \"private_key\"\n                ]\n              }, \n              \"lsync_pub\": {\n                \"get_attr\": [\n                  \"sync_key\", \n                  \"public_key\"\n                ]\n              }, \n              \"wp_auth\": {\n                \"get_attr\": [\n                  \"wp_auth\", \n                  \"value\"\n                ]\n              }, \n              \"version\": {\n                \"get_param\": \"version\"\n              }, \n              \"chef_version\": {\n                \"get_param\": \"chef_version\"\n              }, \n              \"username\": {\n                \"get_param\": \"username\"\n              }, \n              \"wp_web_server_flavor\": {\n                \"get_param\": \"wp_web_server_flavor\"\n              }, \n              \"varnish_master_backend\": {\n                \"get_attr\": [\n                  \"wp_master_server\", \n                  \"networks\", \n                  \"private\", \n                  0\n                ]\n              }, \n              \"parent_stack_id\": {\n                \"get_param\": \"OS::stack_id\"\n              }, \n              \"wp_logged_in\": {\n                \"get_attr\": [\n                  \"wp_logged_in\", \n                  \"value\"\n                ]\n              }, \n              \"kitchen\": {\n                \"get_param\": \"kitchen\"\n              }, \n              \"wp_secure_auth\": {\n                \"get_attr\": [\n                  \"wp_secure_auth\", \n                  \"value\"\n                ]\n              }, \n              \"ssh_keypair_name\": {\n                \"get_resource\": \"ssh_key\"\n              }, \n              \"database_name\": {\n                \"get_param\": \"database_name\"\n              }, \n              \"wp_web_server_hostname\": {\n                \"get_param\": \"wp_web_server_hostnames\"\n              }, \n              \"ssh_public_key\": {\n                \"get_attr\": [\n                  \"ssh_key\", \n                  \"public_key\"\n                ]\n              }, \n              \"database_password\": {\n                \"get_attr\": [\n                  \"database_password\", \n                  \"value\"\n                ]\n              }, \n              \"database_host\": {\n                \"get_attr\": [\n                  \"database_server\", \n                  \"networks\", \n                  \"private\", \n                  0\n                ]\n              }\n            }\n          }\n        }\n      }, \n      \"wp_secure_auth\": {\n        \"type\": \"OS::Heat::RandomString\", \n        \"properties\": {\n          \"length\": 32, \n          \"sequence\": \"hexdigits\"\n        }\n      }, \n      \"mysql_root_password\": {\n        \"type\": \"OS::Heat::RandomString\", \n        \"properties\": {\n          \"length\": 16, \n          \"sequence\": \"lettersdigits\"\n        }\n      }, \n      \"mysql_debian_password\": {\n        \"type\": \"OS::Heat::RandomString\", \n        \"properties\": {\n          \"length\": 16, \n          \"sequence\": \"lettersdigits\"\n        }\n      }, \n      \"wp_auth\": {\n        \"type\": \"OS::Heat::RandomString\", \n        \"properties\": {\n          \"length\": 32, \n          \"sequence\": \"hexdigits\"\n        }\n      }, \n      \"ssh_key\": {\n        \"type\": \"OS::Nova::KeyPair\", \n        \"properties\": {\n          \"name\": {\n            \"get_param\": \"OS::stack_id\"\n          }, \n          \"save_private_key\": true\n        }\n      }, \n      \"wp_master_server\": {\n        \"type\": \"OS::Nova::Server\", \n        \"properties\": {\n          \"key_name\": {\n            \"get_resource\": \"ssh_key\"\n          }, \n          \"flavor\": {\n            \"get_param\": \"wp_master_server_flavor\"\n          }, \n          \"name\": {\n            \"get_param\": \"wp_master_server_hostname\"\n          }, \n          \"image\": {\n            \"get_param\": \"image\"\n          }, \n          \"metadata\": {\n            \"rax-heat\": {\n              \"get_param\": \"OS::stack_id\"\n            }\n          }\n        }\n      }, \n      \"database_server_firewall\": {\n        \"depends_on\": \"wp_master_server_setup\", \n        \"type\": \"OS::Heat::ChefSolo\", \n        \"properties\": {\n          \"username\": \"root\", \n          \"node\": {\n            \"run_list\": [\n              \"recipe[rax-wordpress::memcached-firewall]\"\n            ], \n            \"rax\": {\n              \"memcached\": {\n                \"clients\": [\n                  {\n                    \"get_attr\": [\n                      \"wp_master_server\", \n                      \"networks\", \n                      \"private\", \n                      0\n                    ]\n                  }, \n                  {\n                    \"get_attr\": [\n                      \"wp_web_servers\", \n                      \"privateIPv4\"\n                    ]\n                  }\n                ]\n              }\n            }\n          }, \n          \"private_key\": {\n            \"get_attr\": [\n              \"ssh_key\", \n              \"private_key\"\n            ]\n          }, \n          \"host\": {\n            \"get_attr\": [\n              \"database_server\", \n              \"accessIPv4\"\n            ]\n          }, \n          \"chef_version\": {\n            \"get_param\": \"chef_version\"\n          }, \n          \"kitchen\": {\n            \"get_param\": \"kitchen\"\n          }\n        }\n      }, \n      \"database_server_setup\": {\n        \"depends_on\": \"database_server\", \n        \"type\": \"OS::Heat::ChefSolo\", \n        \"properties\": {\n          \"username\": \"root\", \n          \"node\": {\n            \"rax\": {\n              \"firewall\": {\n                \"tcp\": [\n                  22\n                ]\n              }, \n              \"mysql\": {\n                \"innodb_buffer_pool_mempercent\": 0.6\n              }\n            }, \n            \"memcached\": {\n              \"listen\": {\n                \"get_attr\": [\n                  \"database_server\", \n                  \"networks\", \n                  \"private\", \n                  0\n                ]\n              }, \n              \"memory\": 500\n            }, \n            \"hollandbackup\": {\n              \"main\": {\n                \"mysqldump\": {\n                  \"host\": \"localhost\", \n                  \"password\": {\n                    \"get_attr\": [\n                      \"mysql_root_password\", \n                      \"value\"\n                    ]\n                  }, \n                  \"user\": \"root\"\n                }, \n                \"backup_directory\": \"/var/lib/mysqlbackup\"\n              }\n            }, \n            \"run_list\": [\n              \"recipe[apt]\", \n              \"recipe[build-essential]\", \n              \"recipe[rax-firewall]\", \n              \"recipe[mysql::server]\", \n              \"recipe[rax-wordpress::memcached-firewall]\", \n              \"recipe[memcached]\", \n              \"recipe[rax-wordpress::mysql]\", \n              \"recipe[rax-wordpress::mysql-firewall]\", \n              \"recipe[hollandbackup]\", \n              \"recipe[hollandbackup::mysqldump]\", \n              \"recipe[hollandbackup::main]\", \n              \"recipe[hollandbackup::backupsets]\", \n              \"recipe[hollandbackup::cron]\"\n            ], \n            \"mysql\": {\n              \"remove_test_database\": true, \n              \"root_network_acl\": [\n                \"10.%\"\n              ], \n              \"server_debian_password\": {\n                \"get_attr\": [\n                  \"mysql_debian_password\", \n                  \"value\"\n                ]\n              }, \n              \"server_root_password\": {\n                \"get_attr\": [\n                  \"mysql_root_password\", \n                  \"value\"\n                ]\n              }, \n              \"bind_address\": {\n                \"get_attr\": [\n                  \"database_server\", \n                  \"networks\", \n                  \"private\", \n                  0\n                ]\n              }, \n              \"remove_anonymous_users\": true, \n              \"server_repl_password\": {\n                \"get_attr\": [\n                  \"mysql_repl_password\", \n                  \"value\"\n                ]\n              }\n            }\n          }, \n          \"private_key\": {\n            \"get_attr\": [\n              \"ssh_key\", \n              \"private_key\"\n            ]\n          }, \n          \"host\": {\n            \"get_attr\": [\n              \"database_server\", \n              \"accessIPv4\"\n            ]\n          }, \n          \"chef_version\": {\n            \"get_param\": \"chef_version\"\n          }, \n          \"kitchen\": {\n            \"get_param\": \"kitchen\"\n          }\n        }\n      }, \n      \"wp_master_server_setup\": {\n        \"depends_on\": [\n          \"database_server_setup\", \n          \"wp_web_servers\"\n        ], \n        \"type\": \"OS::Heat::ChefSolo\", \n        \"properties\": {\n          \"username\": \"root\", \n          \"node\": {\n            \"varnish\": {\n              \"version\": \"3.0\", \n              \"listen_port\": \"80\"\n            }, \n            \"sysctl\": {\n              \"values\": {\n                \"fs.inotify.max_user_watches\": 1000000\n              }\n            }, \n            \"lsyncd\": {\n              \"interval\": 5\n            }, \n            \"monit\": {\n              \"mail_format\": {\n                \"from\": \"monit@localhost\"\n              }, \n              \"notify_email\": \"root@localhost\"\n            }, \n            \"vsftpd\": {\n              \"chroot_local_user\": false, \n              \"ssl_ciphers\": \"AES256-SHA\", \n              \"write_enable\": true, \n              \"local_umask\": \"002\", \n              \"hide_ids\": false, \n              \"ssl_enable\": true, \n              \"ipaddress\": \"\"\n            }, \n            \"wordpress\": {\n              \"keys\": {\n                \"logged_in\": {\n                  \"get_attr\": [\n                    \"wp_logged_in\", \n                    \"value\"\n                  ]\n                }, \n                \"secure_auth_key\": {\n                  \"get_attr\": [\n                    \"wp_secure_auth\", \n                    \"value\"\n                  ]\n                }, \n                \"nonce_key\": {\n                  \"get_attr\": [\n                    \"wp_nonce\", \n                    \"value\"\n                  ]\n                }, \n                \"auth\": {\n                  \"get_attr\": [\n                    \"wp_auth\", \n                    \"value\"\n                  ]\n                }\n              }, \n              \"server_aliases\": [\n                {\n                  \"get_param\": \"domain\"\n                }\n              ], \n              \"version\": {\n                \"get_param\": \"version\"\n              }, \n              \"db\": {\n                \"host\": {\n                  \"get_attr\": [\n                    \"database_server\", \n                    \"networks\", \n                    \"private\", \n                    0\n                  ]\n                }, \n                \"pass\": {\n                  \"get_attr\": [\n                    \"database_password\", \n                    \"value\"\n                  ]\n                }, \n                \"user\": {\n                  \"get_param\": \"username\"\n                }, \n                \"name\": {\n                  \"get_param\": \"database_name\"\n                }\n              }, \n              \"dir\": {\n                \"str_replace\": {\n                  \"params\": {\n                    \"%domain%\": {\n                      \"get_param\": \"domain\"\n                    }\n                  }, \n                  \"template\": \"/var/www/vhosts/%domain%\"\n                }\n              }\n            }, \n            \"run_list\": [\n              \"recipe[apt]\",  \n              \"recipe[build-essential]\", \n              \"recipe[mysql::client]\", \n              \"recipe[mysql-chef_gem]\", \n              \"recipe[rax-wordpress::apache-prep]\", \n              \"recipe[sysctl::attribute_driver]\", \n              \"recipe[rax-wordpress::x509]\", \n              \"recipe[php]\", \n              \"recipe[rax-install-packages]\", \n              \"recipe[rax-wordpress::wp-database]\", \n              \"recipe[wordpress]\", \n              \"recipe[rax-wordpress::wp-setup]\", \n              \"recipe[rax-wordpress::user]\", \n              \"recipe[rax-wordpress::memcache]\", \n              \"recipe[lsyncd]\", \n              \"recipe[vsftpd]\", \n              \"recipe[rax-wordpress::vsftpd]\", \n              \"recipe[varnish::repo]\", \n              \"recipe[varnish]\", \n              \"recipe[rax-wordpress::apache]\", \n              \"recipe[rax-wordpress::varnish]\", \n              \"recipe[rax-wordpress::varnish-firewall]\", \n              \"recipe[rax-wordpress::firewall]\", \n              \"recipe[rax-wordpress::vsftpd-firewall]\", \n              \"recipe[rax-wordpress::lsyncd]\"\n            ], \n            \"mysql\": {\n              \"server_root_password\": {\n                \"get_attr\": [\n                  \"mysql_root_password\", \n                  \"value\"\n                ]\n              }, \n              \"bind_address\": {\n                \"get_attr\": [\n                  \"mysql_root_password\", \n                  \"value\"\n                ]\n              }\n            }, \n            \"apache\": {\n              \"listen_ports\": [\n                8080\n              ], \n              \"serversignature\": \"Off\", \n              \"traceenable\": \"Off\", \n              \"timeout\": 30\n            }, \n            \"rax\": {\n              \"varnish\": {\n                \"master_backend\": \"localhost\"\n              }, \n              \"lsyncd\": {\n                \"clients\": {\n                  \"get_attr\": [\n                    \"wp_web_servers\", \n                    \"privateIPv4\"\n                  ]\n                }, \n                \"ssh\": {\n                  \"private_key\": {\n                    \"get_attr\": [\n                      \"sync_key\", \n                      \"private_key\"\n                    ]\n                  }\n                }\n              }, \n              \"memcache\": {\n                \"server\": {\n                  \"get_attr\": [\n                    \"database_server\", \n                    \"networks\", \n                    \"private\", \n                    0\n                  ]\n                }\n              }, \n              \"wordpress\": {\n                \"admin_pass\": {\n                  \"get_attr\": [\n                    \"database_password\", \n                    \"value\"\n                  ]\n                }, \n                \"admin_user\": {\n                  \"get_param\": \"username\"\n                }, \n                \"user\": {\n                  \"group\": {\n                    \"get_param\": \"username\"\n                  }, \n                  \"name\": {\n                    \"get_param\": \"username\"\n                  }\n                }\n              }, \n              \"apache\": {\n                \"domain\": {\n                  \"get_param\": \"domain\"\n                }\n              }, \n              \"packages\": [\n                \"php5-imagick\"\n              ]\n            }\n          }, \n          \"private_key\": {\n            \"get_attr\": [\n              \"ssh_key\", \n              \"private_key\"\n            ]\n          }, \n          \"host\": {\n            \"get_attr\": [\n              \"wp_master_server\", \n              \"accessIPv4\"\n            ]\n          }, \n          \"chef_version\": {\n            \"get_param\": \"chef_version\"\n          }, \n          \"kitchen\": {\n            \"get_param\": \"kitchen\"\n          }\n        }\n      }, \n      \"wp_logged_in\": {\n        \"type\": \"OS::Heat::RandomString\", \n        \"properties\": {\n          \"length\": 32, \n          \"sequence\": \"hexdigits\"\n        }\n      }, \n      \"mysql_repl_password\": {\n        \"type\": \"OS::Heat::RandomString\", \n        \"properties\": {\n          \"length\": 16, \n          \"sequence\": \"lettersdigits\"\n        }\n      }, \n      \"database_password\": {\n        \"type\": \"OS::Heat::RandomString\", \n        \"properties\": {\n          \"length\": 16, \n          \"sequence\": \"lettersdigits\"\n        }\n      }, \n      \"wp_nonce\": {\n        \"type\": \"OS::Heat::RandomString\", \n        \"properties\": {\n          \"length\": 32, \n          \"sequence\": \"hexdigits\"\n        }\n      }\n    }\n  }, \n  \"action\": \"CREATE\", \n  \"project_id\": \"897686\", \n  \"id\": \"cb85fdd9-e25e-441d-83d9-5a526cc86dfe\", \n  \"resources\": {\n    \"load_balancer\": {\n      \"status\": \"COMPLETE\", \n      \"name\": \"load_balancer\", \n      \"resource_data\": {}, \n      \"resource_id\": \"468685\", \n      \"action\": \"CREATE\", \n      \"type\": \"Rackspace::Cloud::LoadBalancer\", \n      \"metadata\": {}\n    }, \n    \"sync_key\": {\n      \"status\": \"COMPLETE\", \n      \"name\": \"sync_key\", \n      \"resource_data\": {\n        \"private_key\": \"-----BEGIN RSA PRIVATE KEY-----\\nMIIEpAIBAAKCAQEAsZ0K0PCNizQ8q6vp5urnVSlS+MCw6qRYI5xLfOSnFZZmt0Hm\\naARR1inV2HBYbv1Qu8IE1N+lHbrd21zXf2YTLe77RN8SNy4D5FQjQt4U1ZgCffg1\\nwvQFqknwJojrIkLYSBPaVAOar8SmDTZLJUe55PJzX/fzGhBcsPAetMUCgBTniEdG\\n2DxHgkXrVpkQeQE2bXYQ/CJ9mYtrk43ee1StPakCgj4c/3BaB9/WVc/6a4FICvfz\\nQHgO1v8a3tAWO4EMYX+yOiVly/3yVR4brlPKqtubbe+L97KBTUUJh4n86aqz1Y6R\\nCfeBI9BZcf9ZFjjVbzSwbH6/Iu7NopwE5y4hmQIDAQABAoIBAB9S2ON8aRoRvllw\\nWjH1X5LvVMi2Av1+umSdXdrK4IS4H6lWH/JcQKqKekJPnekFF8XlM8DvKEmT+SiE\\nuSSotd019m5xAN9maB1OkWFrlTUON/JLYf/d1Vnw7D9/iihirY4YojqK4C77eWV/\\nG8WZXrl34M0eB2ujUxWJY4Dx9bzsp48wxbzMcFQjKg8QWMSfUVkmopkk87fOQEjf\\nXvPcMjqXlz0BYQh1KQxfypf6qNc2wZ+OcPMEnsRNxQLxYOx2Eq0X9bQsfwFEZGQX\\nfTzjLde6AAtuap/RYp5rBr7mAm7AXx55UkuBg4agOsUcP1rEcgfmqpY0fy072iCn\\n29c/xAECgYEA4NdZj1aJfYC2RWyj5ggbpgvucH3EWCdgMFpqndu2PDX/m8XxeTI5\\nYgngVjiAKOTe2dMjwFhEXEu/2GQKwcJd8QgTXIux7P6aoFcSnYcHOEIYZ1cgA60m\\n+cMj4oL8IvcSeow+JRkj+cqA/Pk3hCVr+CeULtnWBQM7YMHpuEdN21kCgYEAyjoz\\npLB5OHktheGTiTfLVwxu3qYoWVjJX9VAq575KZqDwGHUGm+nApb8YMz4nwdUfcKG\\niF7XpnltY7ACPj0t70p7Bim6lsDSEttF+z5einWze44NMcV5AMnWneqIxZkMxoj2\\nCTnKNAVIELx9fSnFtvQ9+dLSx6QKnlkC0po28EECgYEAhWliu/mmNXD1NnaDPhAb\\nj8hOoDMQGRqsKaTM1IQ1Or7zv5ORd8+EWxbvJVn7OcisLuXotc3qKjXMTPL3qwbQ\\nxR98lZJSbgSY7YEdC5m+f/RAFLmOxn+su9C9bz83quud7Fdg3JRxU1uEdBbQiTnH\\nOgUKGU6qfmjvh7coHm841GkCgYEArMF/sKcZR0ctvntv//7r9Jcod4fWXE1e6kFR\\nF8uc6w+WkdiAy3yqXaoCO+eeVKx8X1q4dvMeopaE/m4z3FuDTDKCWkd3oKVkULuF\\nUxZ6ySm3hEtbtjMOJcBHWWwsHzGaGliSZls6A6qnX7TGNxBiWOLZtvuFGQtoDtHX\\neXZIjIECgYAidQi4lWpfAQMZpI/QzZ/IPyd4lkxnGrQppxlFFfPUup7n3M2kcJcW\\nST+GF6JvarxMeH90EnEf9Kez+NpwLCoEM+a1j1jGceRVORWBSbYGAYd32Tp7NdTu\\nVP21wSudvC8+WQOJPNk3rrvoPvRlo0KSeJhjsAJkA/YM7hnE0a26uw==\\n-----END RSA PRIVATE KEY-----\\n\"\n      }, \n      \"resource_id\": \"cb85fdd9-e25e-441d-83d9-5a526cc86dfe-sync\", \n      \"action\": \"CREATE\", \n      \"type\": \"OS::Nova::KeyPair\", \n      \"metadata\": {}\n    }, \n    \"database_server\": {\n      \"status\": \"COMPLETE\", \n      \"name\": \"database_server\", \n      \"resource_data\": {}, \n      \"resource_id\": \"dac59c4f-968b-4f56-9fd1-1586dde45220\", \n      \"action\": \"CREATE\", \n      \"type\": \"OS::Nova::Server\", \n      \"metadata\": {}\n    }, \n    \"wp_web_servers\": {\n      \"status\": \"COMPLETE\", \n      \"name\": \"wordpress1-wp_web_servers-65cpef6rwvm6\", \n      \"stack_user_project_id\": \"897686\", \n      \"environment\": {\n        \"parameter_defaults\": {}, \n        \"parameters\": {}, \n        \"resource_registry\": {\n          \"https://raw.githubusercontent.com/rackspace-orchestration-templates/wordpress-multi/master/wordpress-web-server.yaml\": \"https://raw.githubusercontent.com/rackspace-orchestration-templates/wordpress-multi/master/wordpress-web-server.yaml\", \n          \"resources\": {}\n        }\n      }, \n      \"template\": {\n        \"heat_template_version\": \"2013-05-23\", \n        \"resources\": {\n          \"0\": {\n            \"type\": \"https://raw.githubusercontent.com/rackspace-orchestration-templates/wordpress-multi/master/wordpress-web-server.yaml\", \n            \"properties\": {\n              \"domain\": \"example.com\", \n              \"image\": \"Ubuntu 12.04 LTS (Precise Pangolin) (PVHVM)\", \n              \"wp_nonce\": \"BBCFC317C90AA3CDCBC2047FC22EFCF2\", \n              \"memcached_host\": \"10.209.39.120\", \n              \"prefix\": \"wp_\", \n              \"ssh_private_key\": \"-----BEGIN RSA PRIVATE KEY-----\\nMIIEowIBAAKCAQEAnptZnLM1mdPwC91ZSEY5GnZP+45NlUM+Cc8VO7/grZeHvWLW\\nb9Pb9xX/RsehqzEFkLb/m5ln40ny0yInwcZ5khSc49R0aYAZDBRcPaOzCm9LjhZJ\\nfeURzl7gVD/rwcKF3mXskHZ6W51+Mp3AvRS2g5vaQ2Hf1hF0E42kkH31Grbu5BQ3\\nldwHepHmF0CFjC7x9Q06fFaht3Yf01jScUmjHl+9LOoJSJxbAK0f+25mGTizxhR7\\nL8WnsSP7HE47U7qp5J4OyhnhcNxB4Cq8chGqs7xQL/kPfT6AIAn+rSsmPqpeENyC\\naTZFysD7CfC6HiQbp/pzsgJ9e05VKf6cE7GLwwIDAQABAoIBAE9cPAKESRWnTj0h\\njEL1oCz1dh/QnFFLTAdsbptu7uTtJSZGBjX+M9n2T70CtooKBVbbuhoJMEox/iZW\\nuL3kqX/GgJoe/ACt79pzdZQCDNvzxEJcNHmh3L7+ChEdysEwq/sT1MKUBbVBoJuD\\nA6WYb5p6qUN9/ZoHMaV3AhiqbbHnfQkj7lS7OjeTcXjm5o9YdMGbCe3G+sG+gX28\\nEDfEUw0l4Sw7UqaYKsASkm3kOA1y6mD6GUXFCghKq9/5KAqE2h5BEUnB70YAYotL\\nFWFi197R3F9V0X9gcARMKzuq+h5HBl8lsvYsZe84i0niCxOwjCClY6cC6ZEB6IBO\\ndbonD0ECgYEAyvPJJnM0c/Kv/mVX1rKOrn4ibv04gRojRftL4hmA+3URcDbYu2EH\\nkUM3tfwVZbWnkWbV05a4B4Tkwd4CETbGyKN79EXhyA9RYhPsrpAa8Rajb2daOaTf\\nLgD3YniOJPq8Z5kschuqNYiv6h7Pp+lz0oPwL1TMau7jwA6+DOyEDfUCgYEAyBBD\\nI63aXByqr/Orm2DI46TCm/Zl8hSZ9gpIaUlyQjlhbLvjOMe1IPye7TXRfeiyPIKP\\nFAT8w7rrELCcqv1wALUGALNozi/E49QhUexEWIv4oHJKo/dVpSYI7vVsbszh/2mq\\njR5mLyUJjU7zsMt8wyrF+JKe7bt6zwv1gSiTp9cCgYAkB+HXPK68QwKxxGYyzKJ+\\nIhCU6cnFSdGnU/Tl4CdA/UiqRmJ16cUBKhDS8z0NQJHOQ5aEqQZk91fxfyuYyMPD\\nzRpthJaQAQAuzGDBoP3XfXBoj8253CZvMWa6CbMap5UZQ11bqMOwG2M3yl6NbenN\\nHvVeQczE00KFz1g4TSkonQKBgQCqPSRUfQCddwtLdAanzeDDzRSIkE/JgfxM4A0k\\nAoqGjbs4Ql0kmNOpQS2fXjdoc5UPZm2HtIK9rxWNeyulWMlw4Jk+CWx6Xy2kTIMZ\\n6flye5DSPs8C3Vl0kXvyksZ1NkRtCaZGNQLwxQxuwSseWtlMXd5eGa3BT9I90shS\\n4otauwKBgCKxTTfOTGpsWe89FXNS2h5xhkmeYu7uqeb05FwmM94YUXVvQFfwOgXb\\ne0Zm1PFYW8p2CxGgJCbeC6FmAegXo51seyDxhO1v62HXUbZncH9FD67CvVX5j0qg\\nJAs+tzTslfKMyYam6qVjMceZTWMLUxG93skY06qRoQmwAnEWYUFL\\n-----END RSA PRIVATE KEY-----\\n\", \n              \"lsync_pub\": \"ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCxnQrQ8I2LNDyrq+nm6udVKVL4wLDqpFgjnEt85KcVlma3QeZoBFHWKdXYcFhu/VC7wgTU36Udut3bXNd/ZhMt7vtE3xI3LgPkVCNC3hTVmAJ9+DXC9AWqSfAmiOsiQthIE9pUA5qvxKYNNkslR7nk8nNf9/MaEFyw8B60xQKAFOeIR0bYPEeCRetWmRB5ATZtdhD8In2Zi2uTjd57VK09qQKCPhz/cFoH39ZVz/prgUgK9/NAeA7W/xre0BY7gQxhf7I6JWXL/fJVHhuuU8qq25tt74v3soFNRQmHifzpqrPVjpEJ94Ej0Flx/1kWONVvNLBsfr8i7s2inATnLiGZ Generated-by-Nova\\n\", \n              \"wp_auth\": \"57D02AA0A3A1238DC594C377C0AF9F96\", \n              \"version\": \"3.9.2\", \n              \"chef_version\": \"11.16.2\", \n              \"username\": \"wp_user\", \n              \"wp_web_server_flavor\": \"2 GB General Purpose v1\", \n              \"varnish_master_backend\": \"10.209.39.101\", \n              \"parent_stack_id\": \"cb85fdd9-e25e-441d-83d9-5a526cc86dfe\", \n              \"wp_logged_in\": \"2D948856C2FDF887B9BAD842052EEC16\", \n              \"kitchen\": \"https://github.com/rackspace-orchestration-templates/wordpress-multi\", \n              \"wp_secure_auth\": \"EB179ACEA78F7C3F15AEDF379EC843CA\", \n              \"ssh_keypair_name\": \"cb85fdd9-e25e-441d-83d9-5a526cc86dfe\", \n              \"database_name\": \"wordpress\", \n              \"wp_web_server_hostname\": \"WordPress-Web0\", \n              \"ssh_public_key\": \"ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCem1mcszWZ0/AL3VlIRjkadk/7jk2VQz4JzxU7v+Ctl4e9YtZv09v3Ff9Gx6GrMQWQtv+bmWfjSfLTIifBxnmSFJzj1HRpgBkMFFw9o7MKb0uOFkl95RHOXuBUP+vBwoXeZeyQdnpbnX4yncC9FLaDm9pDYd/WEXQTjaSQffUatu7kFDeV3Ad6keYXQIWMLvH1DTp8VqG3dh/TWNJxSaMeX70s6glInFsArR/7bmYZOLPGFHsvxaexI/scTjtTuqnkng7KGeFw3EHgKrxyEaqzvFAv+Q99PoAgCf6tKyY+ql4Q3IJpNkXKwPsJ8LoeJBun+nOyAn17TlUp/pwTsYvD Generated-by-Nova\\n\", \n              \"database_password\": \"nPuJPH2G4JpUM2NL\", \n              \"database_host\": \"10.209.39.120\"\n            }\n          }\n        }\n      }, \n      \"action\": \"CREATE\", \n      \"project_id\": \"897686\", \n      \"id\": \"cbe55a4b-9f26-4abf-a0f3-4eb67fd59e96\", \n      \"resources\": {\n        \"0\": {\n          \"status\": \"COMPLETE\", \n          \"name\": \"wordpress1-wp_web_servers-65cpef6rwvm6-0-mowt35mxfdyq\", \n          \"stack_user_project_id\": \"897686\", \n          \"environment\": {\n            \"parameter_defaults\": {}, \n            \"parameters\": {\n              \"domain\": \"example.com\", \n              \"image\": \"Ubuntu 12.04 LTS (Precise Pangolin) (PVHVM)\", \n              \"wp_nonce\": \"BBCFC317C90AA3CDCBC2047FC22EFCF2\", \n              \"parent_stack_id\": \"cb85fdd9-e25e-441d-83d9-5a526cc86dfe\", \n              \"prefix\": \"wp_\", \n              \"ssh_private_key\": \"-----BEGIN RSA PRIVATE KEY-----\\nMIIEowIBAAKCAQEAnptZnLM1mdPwC91ZSEY5GnZP+45NlUM+Cc8VO7/grZeHvWLW\\nb9Pb9xX/RsehqzEFkLb/m5ln40ny0yInwcZ5khSc49R0aYAZDBRcPaOzCm9LjhZJ\\nfeURzl7gVD/rwcKF3mXskHZ6W51+Mp3AvRS2g5vaQ2Hf1hF0E42kkH31Grbu5BQ3\\nldwHepHmF0CFjC7x9Q06fFaht3Yf01jScUmjHl+9LOoJSJxbAK0f+25mGTizxhR7\\nL8WnsSP7HE47U7qp5J4OyhnhcNxB4Cq8chGqs7xQL/kPfT6AIAn+rSsmPqpeENyC\\naTZFysD7CfC6HiQbp/pzsgJ9e05VKf6cE7GLwwIDAQABAoIBAE9cPAKESRWnTj0h\\njEL1oCz1dh/QnFFLTAdsbptu7uTtJSZGBjX+M9n2T70CtooKBVbbuhoJMEox/iZW\\nuL3kqX/GgJoe/ACt79pzdZQCDNvzxEJcNHmh3L7+ChEdysEwq/sT1MKUBbVBoJuD\\nA6WYb5p6qUN9/ZoHMaV3AhiqbbHnfQkj7lS7OjeTcXjm5o9YdMGbCe3G+sG+gX28\\nEDfEUw0l4Sw7UqaYKsASkm3kOA1y6mD6GUXFCghKq9/5KAqE2h5BEUnB70YAYotL\\nFWFi197R3F9V0X9gcARMKzuq+h5HBl8lsvYsZe84i0niCxOwjCClY6cC6ZEB6IBO\\ndbonD0ECgYEAyvPJJnM0c/Kv/mVX1rKOrn4ibv04gRojRftL4hmA+3URcDbYu2EH\\nkUM3tfwVZbWnkWbV05a4B4Tkwd4CETbGyKN79EXhyA9RYhPsrpAa8Rajb2daOaTf\\nLgD3YniOJPq8Z5kschuqNYiv6h7Pp+lz0oPwL1TMau7jwA6+DOyEDfUCgYEAyBBD\\nI63aXByqr/Orm2DI46TCm/Zl8hSZ9gpIaUlyQjlhbLvjOMe1IPye7TXRfeiyPIKP\\nFAT8w7rrELCcqv1wALUGALNozi/E49QhUexEWIv4oHJKo/dVpSYI7vVsbszh/2mq\\njR5mLyUJjU7zsMt8wyrF+JKe7bt6zwv1gSiTp9cCgYAkB+HXPK68QwKxxGYyzKJ+\\nIhCU6cnFSdGnU/Tl4CdA/UiqRmJ16cUBKhDS8z0NQJHOQ5aEqQZk91fxfyuYyMPD\\nzRpthJaQAQAuzGDBoP3XfXBoj8253CZvMWa6CbMap5UZQ11bqMOwG2M3yl6NbenN\\nHvVeQczE00KFz1g4TSkonQKBgQCqPSRUfQCddwtLdAanzeDDzRSIkE/JgfxM4A0k\\nAoqGjbs4Ql0kmNOpQS2fXjdoc5UPZm2HtIK9rxWNeyulWMlw4Jk+CWx6Xy2kTIMZ\\n6flye5DSPs8C3Vl0kXvyksZ1NkRtCaZGNQLwxQxuwSseWtlMXd5eGa3BT9I90shS\\n4otauwKBgCKxTTfOTGpsWe89FXNS2h5xhkmeYu7uqeb05FwmM94YUXVvQFfwOgXb\\ne0Zm1PFYW8p2CxGgJCbeC6FmAegXo51seyDxhO1v62HXUbZncH9FD67CvVX5j0qg\\nJAs+tzTslfKMyYam6qVjMceZTWMLUxG93skY06qRoQmwAnEWYUFL\\n-----END RSA PRIVATE KEY-----\\n\", \n              \"lsync_pub\": \"ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCxnQrQ8I2LNDyrq+nm6udVKVL4wLDqpFgjnEt85KcVlma3QeZoBFHWKdXYcFhu/VC7wgTU36Udut3bXNd/ZhMt7vtE3xI3LgPkVCNC3hTVmAJ9+DXC9AWqSfAmiOsiQthIE9pUA5qvxKYNNkslR7nk8nNf9/MaEFyw8B60xQKAFOeIR0bYPEeCRetWmRB5ATZtdhD8In2Zi2uTjd57VK09qQKCPhz/cFoH39ZVz/prgUgK9/NAeA7W/xre0BY7gQxhf7I6JWXL/fJVHhuuU8qq25tt74v3soFNRQmHifzpqrPVjpEJ94Ej0Flx/1kWONVvNLBsfr8i7s2inATnLiGZ Generated-by-Nova\\n\", \n              \"wp_auth\": \"57D02AA0A3A1238DC594C377C0AF9F96\", \n              \"version\": \"3.9.2\", \n              \"chef_version\": \"11.16.2\", \n              \"username\": \"wp_user\", \n              \"wp_web_server_flavor\": \"2 GB General Purpose v1\", \n              \"varnish_master_backend\": \"10.209.39.101\", \n              \"memcached_host\": \"10.209.39.120\", \n              \"wp_logged_in\": \"2D948856C2FDF887B9BAD842052EEC16\", \n              \"kitchen\": \"https://github.com/rackspace-orchestration-templates/wordpress-multi\", \n              \"wp_secure_auth\": \"EB179ACEA78F7C3F15AEDF379EC843CA\", \n              \"ssh_keypair_name\": \"cb85fdd9-e25e-441d-83d9-5a526cc86dfe\", \n              \"database_name\": \"wordpress\", \n              \"wp_web_server_hostname\": \"WordPress-Web0\", \n              \"ssh_public_key\": \"ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCem1mcszWZ0/AL3VlIRjkadk/7jk2VQz4JzxU7v+Ctl4e9YtZv09v3Ff9Gx6GrMQWQtv+bmWfjSfLTIifBxnmSFJzj1HRpgBkMFFw9o7MKb0uOFkl95RHOXuBUP+vBwoXeZeyQdnpbnX4yncC9FLaDm9pDYd/WEXQTjaSQffUatu7kFDeV3Ad6keYXQIWMLvH1DTp8VqG3dh/TWNJxSaMeX70s6glInFsArR/7bmYZOLPGFHsvxaexI/scTjtTuqnkng7KGeFw3EHgKrxyEaqzvFAv+Q99PoAgCf6tKyY+ql4Q3IJpNkXKwPsJ8LoeJBun+nOyAn17TlUp/pwTsYvD Generated-by-Nova\\n\", \n              \"database_password\": \"nPuJPH2G4JpUM2NL\", \n              \"database_host\": \"10.209.39.120\"\n            }, \n            \"resource_registry\": {\n              \"resources\": {}\n            }\n          }, \n          \"template\": {\n            \"outputs\": {\n              \"accessIPv4\": {\n                \"value\": {\n                  \"get_attr\": [\n                    \"wp_web_server\", \n                    \"accessIPv4\"\n                  ]\n                }\n              }, \n              \"privateIPv4\": {\n                \"value\": {\n                  \"get_attr\": [\n                    \"wp_web_server\", \n                    \"networks\", \n                    \"private\", \n                    0\n                  ]\n                }\n              }\n            }, \n            \"heat_template_version\": \"2013-05-23\", \n            \"description\": \"This is a Heat template to deploy a single Linux server running a WordPress.\\n\", \n            \"parameters\": {\n              \"domain\": {\n                \"default\": \"example.com\", \n                \"type\": \"string\", \n                \"description\": \"Domain to be used with WordPress site\"\n              }, \n              \"image\": {\n                \"default\": \"Ubuntu 12.04 LTS (Precise Pangolin) (PVHVM)\", \n                \"type\": \"string\", \n                \"description\": \"Server Image used for all servers.\", \n                \"constraints\": [\n                  {\n                    \"description\": \"Must be a supported operating system.\", \n                    \"allowed_values\": [\n                      \"Ubuntu 12.04 LTS (Precise Pangolin) (PVHVM)\"\n                    ]\n                  }\n                ]\n              }, \n              \"wp_auth\": {\n                \"type\": \"string\"\n              }, \n              \"memcached_host\": {\n                \"default\": \"127.0.0.1\", \n                \"type\": \"string\", \n                \"description\": \"IP/Host of the memcached server\"\n              }, \n              \"prefix\": {\n                \"default\": \"wp_\", \n                \"type\": \"string\", \n                \"description\": \"Prefix to use for\"\n              }, \n              \"ssh_private_key\": {\n                \"type\": \"string\"\n              }, \n              \"lsync_pub\": {\n                \"type\": \"string\", \n                \"description\": \"Public key for lsync configuration\", \n                \"constraints\": null\n              }, \n              \"wp_nonce\": {\n                \"type\": \"string\"\n              }, \n              \"version\": {\n                \"default\": \"3.9.1\", \n                \"type\": \"string\", \n                \"description\": \"Version of WordPress to install\"\n              }, \n              \"chef_version\": {\n                \"default\": \"11.16.2\", \n                \"type\": \"string\", \n                \"description\": \"Version of chef client to use\"\n              }, \n              \"username\": {\n                \"default\": \"wp_user\", \n                \"type\": \"string\", \n                \"description\": \"Username for system, database, and WordPress logins.\"\n              }, \n              \"wp_web_server_flavor\": {\n                \"default\": \"2 GB General Purpose v1\", \n                \"type\": \"string\", \n                \"description\": \"Web Cloud Server flavor\", \n                \"constraints\": [\n                  {\n                    \"description\": \"Must be a valid Rackspace Cloud Server flavor for the region you have\\nselected to deploy into.\\n\", \n                    \"allowed_values\": [\n                      \"1 GB General Purpose v1\", \n                      \"2 GB General Purpose v1\", \n                      \"4 GB General Purpose v1\", \n                      \"8 GB General Purpose v1\", \n                      \"15 GB I/O v1\", \n                      \"30 GB I/O v1\", \n                      \"1GB Standard Instance\", \n                      \"2GB Standard Instance\", \n                      \"4GB Standard Instance\", \n                      \"8GB Standard Instance\", \n                      \"15GB Standard Instance\", \n                      \"30GB Standard Instance\"\n                    ]\n                  }\n                ]\n              }, \n              \"varnish_master_backend\": {\n                \"default\": \"localhost\", \n                \"type\": \"string\", \n                \"description\": \"Master backend host for admin calls in Varnish\"\n              }, \n              \"parent_stack_id\": {\n                \"default\": \"none\", \n                \"type\": \"string\", \n                \"description\": \"Stack id of the parent stack\"\n              }, \n              \"wp_logged_in\": {\n                \"type\": \"string\"\n              }, \n              \"kitchen\": {\n                \"default\": \"https://github.com/rackspace-orchestration-templates/wordpress-multi\", \n                \"type\": \"string\", \n                \"description\": \"URL for the kitchen to use\"\n              }, \n              \"wp_secure_auth\": {\n                \"type\": \"string\"\n              }, \n              \"ssh_keypair_name\": {\n                \"type\": \"string\", \n                \"description\": \"keypair name to register with Nova for the root SSH key\"\n              }, \n              \"database_name\": {\n                \"default\": \"wordpress\", \n                \"type\": \"string\", \n                \"description\": \"WordPress database name\"\n              }, \n              \"wp_web_server_hostname\": {\n                \"default\": \"WordPress-Web\", \n                \"type\": \"string\", \n                \"description\": \"WordPress Web Server Name\", \n                \"constraints\": [\n                  {\n                    \"length\": {\n                      \"max\": 64, \n                      \"min\": 1\n                    }\n                  }, \n                  {\n                    \"allowed_pattern\": \"^[a-zA-Z][a-zA-Z0-9-]*$\", \n                    \"description\": \"Must begin with a letter and contain only alphanumeric characters.\\n\"\n                  }\n                ]\n              }, \n              \"ssh_public_key\": {\n                \"type\": \"string\"\n              }, \n              \"database_password\": {\n                \"type\": \"string\", \n                \"description\": \"Password to use for database connections.\"\n              }, \n              \"database_host\": {\n                \"default\": \"127.0.0.1\", \n                \"type\": \"string\", \n                \"description\": \"IP/Host of the database server\"\n              }\n            }, \n            \"resources\": {\n              \"wp_web_server_setup\": {\n                \"depends_on\": \"wp_web_server\", \n                \"type\": \"OS::Heat::ChefSolo\", \n                \"properties\": {\n                  \"username\": \"root\", \n                  \"node\": {\n                    \"apache\": {\n                      \"listen_ports\": [\n                        8080\n                      ], \n                      \"serversignature\": \"Off\", \n                      \"traceenable\": \"Off\", \n                      \"timeout\": 30\n                    }, \n                    \"varnish\": {\n                      \"version\": \"3.0\", \n                      \"listen_port\": \"80\"\n                    }, \n                    \"wordpress\": {\n                      \"keys\": {\n                        \"logged_in\": {\n                          \"get_param\":  \"wp_logged_in\"\n                        }, \n                        \"secure_auth_key\": {\n                          \"get_param\": \"wp_secure_auth\"\n                        }, \n                        \"nonce_key\": {\n                          \"get_param\": \"wp_nonce\"\n                        }, \n                        \"auth\": {\n                          \"get_param\": \"wp_auth\"\n                        }\n                      }, \n                      \"server_aliases\": [\n                        {\n                          \"get_param\": \"domain\"\n                        }\n                      ], \n                      \"version\": {\n                        \"get_param\": \"version\"\n                      }, \n                      \"db\": {\n                        \"host\": {\n                          \"get_param\": \"database_host\"\n                        }, \n                        \"user\": {\n                          \"get_param\": \"username\"\n                        }, \n                        \"name\": {\n                          \"get_param\": \"database_name\"\n                        }, \n                        \"pass\": {\n                          \"get_param\": \"database_password\"\n                        }\n                       }, \n                      \"dir\": {\n                        \"str_replace\": {\n                          \"params\": {\n                            \"%domain%\": {\n                              \"get_param\": \"domain\"\n                            }\n                          }, \n                          \"template\": \"/var/www/vhosts/%domain%\"\n                        }\n                      }\n                    }, \n                    \"rax\": {\n                      \"varnish\": {\n                        \"master_backend\": {\n                          \"get_param\": \"varnish_master_backend\"\n                        }\n                      }, \n                      \"lsyncd\": {\n                        \"ssh\": {\n                          \"pub\": {\n                            \"get_param\": \"lsync_pub\"\n                          }\n                        }\n                      }, \n                      \"memcache\": {\n                        \"server\": {\n                          \"get_param\": \"memcached_host\"\n                        }\n                      }, \n                      \"wordpress\": {\n                        \"admin_pass\": {\n                          \"get_param\": \"database_password\"\n                        }, \n                        \"user\": {\n                          \"group\": {\n                            \"get_param\": \"username\"\n                          }, \n                          \"name\": {\n                            \"get_param\": \"username\"\n                          }\n                        }\n                      }, \n                      \"apache\": {\n                        \"domain\": {\n                          \"get_param\": \"domain\"\n                        }\n                      }, \n                      \"packages\": [\n                        \"php5-imagick\"\n                      ]\n                    }, \n                    \"run_list\": [\n                      \"recipe[apt]\", \n                      \"recipe[build-essential]\", \n                      \"recipe[rax-wordpress::apache-prep]\", \n                      \"recipe[rax-wordpress::x509]\", \n                      \"recipe[php]\", \n                      \"recipe[rax-install-packages]\", \n                      \"recipe[wordpress]\", \n                      \"recipe[rax-wordpress::user]\", \n                      \"recipe[rax-wordpress::memcache]\", \n                      \"recipe[varnish::repo]\", \n                      \"recipe[varnish]\", \n                      \"recipe[rax-wordpress::apache]\", \n                      \"recipe[rax-wordpress::varnish]\", \n                      \"recipe[rax-wordpress::firewall]\", \n                      \"recipe[rax-wordpress::lsyncd-client]\"\n                    ]\n                  }, \n                  \"private_key\": {\n                    \"get_param\": \"ssh_private_key\"\n                  }, \n                  \"host\": {\n                    \"get_attr\": [\n                      \"wp_web_server\", \n                      \"accessIPv4\"\n                    ]\n                  }, \n                  \"chef_version\": {\n                    \"get_param\": \"chef_version\"\n                  }, \n                  \"kitchen\": {\n                    \"get_param\": \"kitchen\"\n                  }\n                }\n              }, \n              \"wp_web_server\": {\n                \"type\": \"OS::Nova::Server\", \n                \"properties\": {\n                  \"key_name\": {\n                    \"get_param\": \"ssh_keypair_name\"\n                  }, \n                  \"flavor\": {\n                    \"get_param\": \"wp_web_server_flavor\"\n                  }, \n                  \"name\": {\n                    \"get_param\": \"wp_web_server_hostname\"\n                  }, \n                  \"image\": {\n                    \"get_param\": \"image\"\n                  }, \n                  \"metadata\": {\n                    \"rax-heat\": {\n                      \"get_param\": \"parent_stack_id\"\n                    }\n                  }\n                }\n              }\n            }\n          }, \n          \"action\": \"CREATE\", \n          \"project_id\": \"897686\", \n          \"id\": \"4a5919e8-f72f-4ea5-8671-30d0582b8c16\", \n          \"resources\": {\n            \"wp_web_server_setup\": {\n              \"status\": \"COMPLETE\", \n              \"name\": \"wp_web_server_setup\", \n              \"resource_data\": {\n                \"process_id\": \"25121\"\n              }, \n              \"resource_id\": \"63481508-bd29-4958-a5aa-5d9906d9472f\", \n              \"action\": \"CREATE\", \n              \"type\": \"OS::Heat::ChefSolo\", \n              \"metadata\": {}\n            }, \n            \"wp_web_server\": {\n              \"status\": \"COMPLETE\", \n              \"name\": \"wp_web_server\", \n              \"resource_data\": {}, \n              \"resource_id\": \"4bdca95f-0ed4-4a14-aa56-1642613e31b2\", \n              \"action\": \"CREATE\", \n              \"type\": \"OS::Nova::Server\", \n              \"metadata\": {}\n            }\n          }\n        }\n      }\n    }, \n    \"wp_secure_auth\": {\n      \"status\": \"COMPLETE\", \n      \"name\": \"wp_secure_auth\", \n      \"resource_data\": {\n        \"value\": \"EB179ACEA78F7C3F15AEDF379EC843CA\"\n      }, \n      \"resource_id\": \"wordpress1-wp_secure_auth-ogszzqwpf6le\", \n      \"action\": \"CREATE\", \n      \"type\": \"OS::Heat::RandomString\", \n      \"metadata\": {}\n    }, \n    \"mysql_root_password\": {\n      \"status\": \"COMPLETE\", \n      \"name\": \"mysql_root_password\", \n      \"resource_data\": {\n        \"value\": \"ekFQCweXC8I5Tbow\"\n      }, \n      \"resource_id\": \"wordpress1-mysql_root_password-mhbrknatmbhf\", \n      \"action\": \"CREATE\", \n      \"type\": \"OS::Heat::RandomString\", \n      \"metadata\": {}\n    }, \n    \"mysql_debian_password\": {\n      \"status\": \"COMPLETE\", \n      \"name\": \"mysql_debian_password\", \n      \"resource_data\": {\n        \"value\": \"2tp5zUKAHScgAgaO\"\n      }, \n      \"resource_id\": \"wordpress1-mysql_debian_password-nnvp54d34qg6\", \n      \"action\": \"CREATE\", \n      \"type\": \"OS::Heat::RandomString\", \n      \"metadata\": {}\n    }, \n    \"wp_auth\": {\n      \"status\": \"COMPLETE\", \n      \"name\": \"wp_auth\", \n      \"resource_data\": {\n        \"value\": \"57D02AA0A3A1238DC594C377C0AF9F96\"\n      }, \n      \"resource_id\": \"wordpress1-wp_auth-yqcs263pi6mc\", \n      \"action\": \"CREATE\", \n      \"type\": \"OS::Heat::RandomString\", \n      \"metadata\": {}\n    }, \n    \"ssh_key\": {\n      \"status\": \"COMPLETE\", \n      \"name\": \"ssh_key\", \n      \"resource_data\": {\n        \"private_key\": \"-----BEGIN RSA PRIVATE KEY-----\\nMIIEowIBAAKCAQEAnptZnLM1mdPwC91ZSEY5GnZP+45NlUM+Cc8VO7/grZeHvWLW\\nb9Pb9xX/RsehqzEFkLb/m5ln40ny0yInwcZ5khSc49R0aYAZDBRcPaOzCm9LjhZJ\\nfeURzl7gVD/rwcKF3mXskHZ6W51+Mp3AvRS2g5vaQ2Hf1hF0E42kkH31Grbu5BQ3\\nldwHepHmF0CFjC7x9Q06fFaht3Yf01jScUmjHl+9LOoJSJxbAK0f+25mGTizxhR7\\nL8WnsSP7HE47U7qp5J4OyhnhcNxB4Cq8chGqs7xQL/kPfT6AIAn+rSsmPqpeENyC\\naTZFysD7CfC6HiQbp/pzsgJ9e05VKf6cE7GLwwIDAQABAoIBAE9cPAKESRWnTj0h\\njEL1oCz1dh/QnFFLTAdsbptu7uTtJSZGBjX+M9n2T70CtooKBVbbuhoJMEox/iZW\\nuL3kqX/GgJoe/ACt79pzdZQCDNvzxEJcNHmh3L7+ChEdysEwq/sT1MKUBbVBoJuD\\nA6WYb5p6qUN9/ZoHMaV3AhiqbbHnfQkj7lS7OjeTcXjm5o9YdMGbCe3G+sG+gX28\\nEDfEUw0l4Sw7UqaYKsASkm3kOA1y6mD6GUXFCghKq9/5KAqE2h5BEUnB70YAYotL\\nFWFi197R3F9V0X9gcARMKzuq+h5HBl8lsvYsZe84i0niCxOwjCClY6cC6ZEB6IBO\\ndbonD0ECgYEAyvPJJnM0c/Kv/mVX1rKOrn4ibv04gRojRftL4hmA+3URcDbYu2EH\\nkUM3tfwVZbWnkWbV05a4B4Tkwd4CETbGyKN79EXhyA9RYhPsrpAa8Rajb2daOaTf\\nLgD3YniOJPq8Z5kschuqNYiv6h7Pp+lz0oPwL1TMau7jwA6+DOyEDfUCgYEAyBBD\\nI63aXByqr/Orm2DI46TCm/Zl8hSZ9gpIaUlyQjlhbLvjOMe1IPye7TXRfeiyPIKP\\nFAT8w7rrELCcqv1wALUGALNozi/E49QhUexEWIv4oHJKo/dVpSYI7vVsbszh/2mq\\njR5mLyUJjU7zsMt8wyrF+JKe7bt6zwv1gSiTp9cCgYAkB+HXPK68QwKxxGYyzKJ+\\nIhCU6cnFSdGnU/Tl4CdA/UiqRmJ16cUBKhDS8z0NQJHOQ5aEqQZk91fxfyuYyMPD\\nzRpthJaQAQAuzGDBoP3XfXBoj8253CZvMWa6CbMap5UZQ11bqMOwG2M3yl6NbenN\\nHvVeQczE00KFz1g4TSkonQKBgQCqPSRUfQCddwtLdAanzeDDzRSIkE/JgfxM4A0k\\nAoqGjbs4Ql0kmNOpQS2fXjdoc5UPZm2HtIK9rxWNeyulWMlw4Jk+CWx6Xy2kTIMZ\\n6flye5DSPs8C3Vl0kXvyksZ1NkRtCaZGNQLwxQxuwSseWtlMXd5eGa3BT9I90shS\\n4otauwKBgCKxTTfOTGpsWe89FXNS2h5xhkmeYu7uqeb05FwmM94YUXVvQFfwOgXb\\ne0Zm1PFYW8p2CxGgJCbeC6FmAegXo51seyDxhO1v62HXUbZncH9FD67CvVX5j0qg\\nJAs+tzTslfKMyYam6qVjMceZTWMLUxG93skY06qRoQmwAnEWYUFL\\n-----END RSA PRIVATE KEY-----\\n\"\n      }, \n      \"resource_id\": \"cb85fdd9-e25e-441d-83d9-5a526cc86dfe\", \n      \"action\": \"CREATE\", \n      \"type\": \"OS::Nova::KeyPair\", \n      \"metadata\": {}\n    }, \n    \"wp_master_server\": {\n      \"status\": \"COMPLETE\", \n      \"name\": \"wp_master_server\", \n      \"resource_data\": {}, \n      \"resource_id\": \"730cf391-b5de-4f43-ab3d-1b5e9d05ab10\", \n      \"action\": \"CREATE\", \n      \"type\": \"OS::Nova::Server\", \n      \"metadata\": {}\n    }, \n    \"database_server_firewall\": {\n      \"status\": \"COMPLETE\", \n      \"name\": \"database_server_firewall\", \n      \"resource_data\": {\n        \"process_id\": \"25559\"\n      }, \n      \"resource_id\": \"c445ff25-4f25-4aa6-a63b-b41688a50fe3\", \n      \"action\": \"CREATE\", \n      \"type\": \"OS::Heat::ChefSolo\", \n      \"metadata\": {}\n    }, \n    \"database_server_setup\": {\n      \"status\": \"COMPLETE\", \n      \"name\": \"database_server_setup\", \n      \"resource_data\": {\n        \"process_id\": \"24999\"\n      }, \n      \"resource_id\": \"6b3725f5-2dd9-449a-8003-a52acef85e78\", \n      \"action\": \"CREATE\", \n      \"type\": \"OS::Heat::ChefSolo\", \n      \"metadata\": {}\n    }, \n    \"wp_master_server_setup\": {\n      \"status\": \"COMPLETE\", \n      \"name\": \"wp_master_server_setup\", \n      \"resource_data\": {\n        \"process_id\": \"25359\"\n      }, \n      \"resource_id\": \"b4d7234a-bdce-46bc-a9cb-b5ba530feeeb\", \n      \"action\": \"CREATE\", \n      \"type\": \"OS::Heat::ChefSolo\", \n      \"metadata\": {}\n    }, \n    \"wp_logged_in\": {\n      \"status\": \"COMPLETE\", \n      \"name\": \"wp_logged_in\", \n      \"resource_data\": {\n        \"value\": \"2D948856C2FDF887B9BAD842052EEC16\"\n      }, \n      \"resource_id\": \"wordpress1-wp_logged_in-3kbbq6x7yklc\", \n      \"action\": \"CREATE\", \n      \"type\": \"OS::Heat::RandomString\", \n      \"metadata\": {}\n    }, \n    \"mysql_repl_password\": {\n      \"status\": \"COMPLETE\", \n      \"name\": \"mysql_repl_password\", \n      \"resource_data\": {\n        \"value\": \"z49eosYTXl5uOo4C\"\n      }, \n      \"resource_id\": \"wordpress1-mysql_repl_password-hulbd7654fr2\", \n      \"action\": \"CREATE\", \n      \"type\": \"OS::Heat::RandomString\", \n      \"metadata\": {}\n    }, \n    \"database_password\": {\n      \"status\": \"COMPLETE\", \n      \"name\": \"database_password\", \n      \"resource_data\": {\n        \"value\": \"nPuJPH2G4JpUM2NL\"\n      }, \n      \"resource_id\": \"wordpress1-database_password-cs2htyy4lao7\", \n      \"action\": \"CREATE\", \n      \"type\": \"OS::Heat::RandomString\", \n      \"metadata\": {}\n    }, \n    \"wp_nonce\": {\n      \"status\": \"COMPLETE\", \n      \"name\": \"wp_nonce\", \n      \"resource_data\": {\n        \"value\": \"BBCFC317C90AA3CDCBC2047FC22EFCF2\"\n      }, \n      \"resource_id\": \"wordpress1-wp_nonce-dziqrobv34ot\", \n      \"action\": \"CREATE\", \n      \"type\": \"OS::Heat::RandomString\", \n      \"metadata\": {}\n    }\n  }\n}\n", "environment": {}}
"""

adopt_data4 = """
{
  "status": "COMPLETE",
  "name": "blah",
  "stack_user_project_id": "883286",
  "environment": {
    "parameter_defaults": {},
    "parameters": {},
    "resource_registry": {
      "https://raw.githubusercontent.com/rackspace-orchestration-templates/wordpress-multi/master/wordpress-web-server.yaml": "https://raw.githubusercontent.com/rackspace-orchestration-templates/wordpress-multi/master/wordpress-web-server.yaml",
      "resources": {}
    }
  },
  "template": {
    "parameter_groups": [
      {
        "parameters": [
          "image"
        ],
        "label": "Server Settings"
      },
      {
        "parameters": [
          "wp_master_server_flavor",
          "wp_web_server_count",
          "wp_web_server_flavor"
        ],
        "label": "Web Server Settings"
      },
      {
        "parameters": [
          "database_server_flavor"
        ],
        "label": "Database Settings"
      },
      {
        "parameters": [
          "domain",
          "username"
        ],
        "label": "WordPress Settings"
      },
      {
        "parameters": [
          "kitchen",
          "chef_version",
          "child_template",
          "version",
          "prefix",
          "load_balancer_hostname",
          "wp_web_server_hostnames",
          "wp_master_server_hostname",
          "database_server_hostname"
        ],
        "label": "rax-dev-params"
      }
    ],
    "heat_template_version": "2013-05-23",
    "description": "This is a Heat template to deploy Load Balanced WordPress servers with a\nbackend database server.\n",
    "parameters": {
      "username": {
        "default": "wp_user",
        "constraints": [
          {
            "allowed_pattern": "^[a-zA-Z0-9 _.@-]{1,16}$",
            "description": "Must be shorter than 16 characters and may only contain alphanumeric\ncharacters, ' ', '_', '.', '@', and/or '-'.\n"
          }
        ],
        "type": "string",
        "description": "Username for system, database, and WordPress logins.",
        "label": "Username"
      },
      "domain": {
        "default": "example.com",
        "constraints": [
          {
            "allowed_pattern": "^[a-zA-Z0-9.-]{1,255}.[a-zA-Z]{2,15}$",
            "description": "Must be a valid domain name"
          }
        ],
        "type": "string",
        "description": "Domain to be used with this WordPress site",
        "label": "Site Domain"
      },
      "chef_version": {
        "default": "11.16.2",
        "type": "string",
        "description": "Version of chef client to use",
        "label": "Chef Version"
      },
      "wp_web_server_flavor": {
        "default": "2 GB General Purpose v1",
        "constraints": [
          {
            "description": "Must be a valid Rackspace Cloud Server flavor for the region you have\nselected to deploy into.\n",
            "allowed_values": [
              "1 GB General Purpose v1",
              "2 GB General Purpose v1",
              "4 GB General Purpose v1",
              "8 GB General Purpose v1",
              "15 GB I/O v1",
              "30 GB I/O v1",
              "1GB Standard Instance",
              "2GB Standard Instance",
              "4GB Standard Instance",
              "8GB Standard Instance",
              "15GB Standard Instance",
              "30GB Standard Instance"
            ]
          }
        ],
        "type": "string",
        "description": "Cloud Server size to use on all of the additional web nodes.\n",
        "label": "Node Server Size"
      },
      "wp_web_server_hostnames": {
        "default": "WordPress-Web%index%",
        "constraints": [
          {
            "length": {
              "max": 64,
              "min": 1
            }
          },
          {
            "allowed_pattern": "^[a-zA-Z][a-zA-Z0-9%-]*$",
            "description": "Must begin with a letter and contain only alphanumeric characters.\n"
          }
        ],
        "type": "string",
        "description": "Hostname to use for all additional WordPress web nodes",
        "label": "Server Name"
      },
      "image": {
        "default": "Ubuntu 12.04 LTS (Precise Pangolin) (PVHVM)",
        "constraints": [
          {
            "description": "Must be a supported operating system.",
            "allowed_values": [
              "Ubuntu 12.04 LTS (Precise Pangolin) (PVHVM)"
            ]
          }
        ],
        "type": "string",
        "description": "Required: Server image used for all servers that are created as a part of\nthis deployment.\n",
        "label": "Operating System"
      },
      "load_balancer_hostname": {
        "default": "WordPress-Load-Balancer",
        "constraints": [
          {
            "length": {
              "max": 64,
              "min": 1
            }
          },
          {
            "allowed_pattern": "^[a-zA-Z][a-zA-Z0-9-]*$",
            "description": "Must begin with a letter and contain only alphanumeric characters.\n"
          }
        ],
        "type": "string",
        "description": "Hostname for the Cloud Load Balancer",
        "label": "Load Balancer Hostname"
      },
      "database_server_hostname": {
        "default": "WordPress-Database",
        "constraints": [
          {
            "length": {
              "max": 64,
              "min": 1
            }
          },
          {
            "allowed_pattern": "^[a-zA-Z][a-zA-Z0-9-]*$",
            "description": "Must begin with a letter and contain only alphanumeric characters.\n"
          }
        ],
        "type": "string",
        "description": "Hostname to use for your WordPress Database Server",
        "label": "Server Name"
      },
      "wp_master_server_hostname": {
        "default": "WordPress-Master",
        "constraints": [
          {
            "length": {
              "max": 64,
              "min": 1
            }
          },
          {
            "allowed_pattern": "^[a-zA-Z][a-zA-Z0-9-]*$",
            "description": "Must begin with a letter and contain only alphanumeric characters.\n"
          }
        ],
        "type": "string",
        "description": "Hostname to use for your WordPress web-master server.",
        "label": "Server Name"
      },
      "prefix": {
        "default": "wp_",
        "constraints": [
          {
            "allowed_pattern": "^[0-9a-zA-Z$_]{0,10}$",
            "description": "Prefix must be shorter than 10 characters, and can only include\nletters, numbers, $, and/or underscores.\n"
          }
        ],
        "type": "string",
        "description": "Prefix to use for database table names.",
        "label": "Wordpress Prefix"
      },
      "version": {
        "default": "3.9.2",
        "constraints": [
          {
            "allowed_values": [
              "3.9.2"
            ]
          }
        ],
        "type": "string",
        "description": "Version of WordPress to install",
        "label": "WordPress Version"
      },
      "wp_master_server_flavor": {
        "default": "2 GB General Purpose v1",
        "constraints": [
          {
            "description": "Must be a valid Rackspace Cloud Server flavor for the region you have\nselected to deploy into.\n",
            "allowed_values": [
              "1 GB General Purpose v1",
              "2 GB General Purpose v1",
              "4 GB General Purpose v1",
              "8 GB General Purpose v1",
              "15 GB I/O v1",
              "30 GB I/O v1",
              "1GB Standard Instance",
              "2GB Standard Instance",
              "4GB Standard Instance",
              "8GB Standard Instance",
              "15GB Standard Instance",
              "30GB Standard Instance"
            ]
          }
        ],
        "type": "string",
        "description": "Cloud Server size to use for the web-master node. The size should be at\nleast one size larger than what you use for the web nodes. This server\nhandles all admin calls and will ensure files are synced across all\nother nodes.\n",
        "label": "Master Server Size"
      },
      "database_name": {
        "default": "wordpress",
        "constraints": [
          {
            "allowed_pattern": "^[0-9a-zA-Z$_]{1,64}$",
            "description": "Maximum length of 64 characters, may only contain letters, numbers, and\nunderscores.\n"
          }
        ],
        "type": "string",
        "description": "WordPress database name",
        "label": "Database Name"
      },
      "wp_web_server_count": {
        "default": 1,
        "constraints": [
          {
            "range": {
              "max": 7,
              "min": 0
            },
            "description": "Must be between 0 and 7 servers."
          }
        ],
        "type": "number",
        "description": "Number of web servers to deploy in addition to the web-master",
        "label": "Web Server Count"
      },
      "database_server_flavor": {
        "default": "4 GB General Purpose v1",
        "constraints": [
          {
            "description": "Must be a valid Rackspace Cloud Server flavor for the region you have\nselected to deploy into.\n",
            "allowed_values": [
              "2 GB General Purpose v1",
              "4 GB General Purpose v1",
              "8 GB General Purpose v1",
              "15 GB I/O v1",
              "30 GB I/O v1",
              "2GB Standard Instance",
              "4GB Standard Instance",
              "8GB Standard Instance",
              "15GB Standard Instance",
              "30GB Standard Instance"
            ]
          }
        ],
        "type": "string",
        "description": "Cloud Server size to use for the database server. Sizes refer to the\namount of RAM allocated to the server.\n",
        "label": "Server Size"
      },
      "child_template": {
        "default": "https://raw.githubusercontent.com/rackspace-orchestration-templates/wordpress-multi/master/wordpress-web-server.yaml",
        "type": "string",
        "description": "Location of the child template to use for the WordPress web servers\n",
        "label": "Child Template"
      },
      "kitchen": {
        "default": "https://github.com/rackspace-orchestration-templates/wordpress-multi",
        "type": "string",
        "description": "URL for the kitchen to use, fetched using git\n",
        "label": "Kitchen"
      }
    },
    "outputs": {
      "private_key": {
        "description": "SSH Private IP",
        "value": {
          "get_attr": [
            "ssh_key",
            "private_key"
          ]
        }
      },
      "load_balancer_ip": {
        "description": "Load Balancer IP",
        "value": {
          "get_attr": [
            "load_balancer",
            "PublicIp"
          ]
        }
      },
      "mysql_root_password": {
        "description": "MySQL Root Password",
        "value": {
          "get_attr": [
            "mysql_root_password",
            "value"
          ]
        }
      },
      "wordpress_user": {
        "description": "WordPress User",
        "value": {
          "get_param": "username"
        }
      },
      "wordpress_web_ips": {
        "description": "Web Server IPs",
        "value": {
          "get_attr": [
            "wp_web_servers",
            "accessIPv4"
          ]
        }
      },
      "wordpress_password": {
        "description": "WordPress Password",
        "value": {
          "get_attr": [
            "database_password",
            "value"
          ]
        }
      },
      "database_server_ip": {
        "description": "Database Server IP",
        "value": {
          "get_attr": [
            "database_server",
            "accessIPv4"
          ]
        }
      },
      "wordpress_web_master_ip": {
        "description": "Web-Master IP",
        "value": {
          "get_attr": [
            "wp_master_server",
            "accessIPv4"
          ]
        }
      }
    },
    "resources": {
      "load_balancer": {
        "depends_on": [
          "wp_master_server_setup",
          "wp_web_servers"
        ],
        "type": "Rackspace::Cloud::LoadBalancer",
        "properties": {
          "protocol": "HTTP",
          "name": {
            "get_param": "load_balancer_hostname"
          },
          "algorithm": "ROUND_ROBIN",
          "virtualIps": [
            {
              "ipVersion": "IPV4",
              "type": "PUBLIC"
            }
          ],
          "contentCaching": "ENABLED",
          "healthMonitor": {
            "attemptsBeforeDeactivation": 2,
            "statusRegex": "^[23]0[0-2]$",
            "delay": 10,
            "timeout": 5,
            "path": "/",
            "type": "HTTP"
          },
          "nodes": [
            {
              "addresses": [
                {
                  "get_attr": [
                    "wp_master_server",
                    "networks",
                    "private",
                    0
                  ]
                }
              ],
              "condition": "ENABLED",
              "port": 80
            },
            {
              "addresses": {
                "get_attr": [
                  "wp_web_servers",
                  "privateIPv4"
                ]
              },
              "condition": "ENABLED",
              "port": 80
            }
          ],
          "port": 80,
          "metadata": {
            "rax-heat": {
              "get_param": "OS::stack_id"
            }
          }
        }
      },
      "sync_key": {
        "type": "OS::Nova::KeyPair",
        "properties": {
          "name": {
            "str_replace": {
              "params": {
                "%stack_id%": {
                  "get_param": "OS::stack_id"
                }
              },
              "template": "%stack_id%-sync"
            }
          },
          "save_private_key": true
        }
      },
      "database_server": {
        "type": "OS::Nova::Server",
        "properties": {
          "key_name": {
            "get_resource": "ssh_key"
          },
          "flavor": {
            "get_param": "database_server_flavor"
          },
          "name": {
            "get_param": "database_server_hostname"
          },
          "image": {
            "get_param": "image"
          },
          "metadata": {
            "rax-heat": {
              "get_param": "OS::stack_id"
            }
          }
        }
      },
      "wp_web_servers": {
        "depends_on": "database_server",
        "type": "OS::Heat::ResourceGroup",
        "properties": {
          "count": {
            "get_param": "wp_web_server_count"
          },
          "resource_def": {
            "type": {
              "get_param": "child_template"
            },
            "properties": {
              "domain": {
                "get_param": "domain"
              },
              "image": {
                "get_param": "image"
              },
              "wp_nonce": {
                "get_attr": [
                  "wp_nonce",
                  "value"
                ]
              },
              "memcached_host": {
                "get_attr": [
                  "database_server",
                  "networks",
                  "private",
                  0
                ]
              },
              "prefix": {
                "get_param": "prefix"
              },
              "ssh_private_key": {
                "get_attr": [
                  "ssh_key",
                  "private_key"
                ]
              },
              "lsync_pub": {
                "get_attr": [
                  "sync_key",
                  "public_key"
                ]
              },
              "wp_auth": {
                "get_attr": [
                  "wp_auth",
                  "value"
                ]
              },
              "version": {
                "get_param": "version"
              },
              "chef_version": {
                "get_param": "chef_version"
              },
              "username": {
                "get_param": "username"
              },
              "wp_web_server_flavor": {
                "get_param": "wp_web_server_flavor"
              },
              "varnish_master_backend": {
                "get_attr": [
                  "wp_master_server",
                  "networks",
                  "private",
                  0
                ]
              },
              "parent_stack_id": {
                "get_param": "OS::stack_id"
              },
              "wp_logged_in": {
                "get_attr": [
                  "wp_logged_in",
                  "value"
                ]
              },
              "kitchen": {
                "get_param": "kitchen"
              },
              "wp_secure_auth": {
                "get_attr": [
                  "wp_secure_auth",
                  "value"
                ]
              },
              "ssh_keypair_name": {
                "get_resource": "ssh_key"
              },
              "database_name": {
                "get_param": "database_name"
              },
              "wp_web_server_hostname": {
                "get_param": "wp_web_server_hostnames"
              },
              "ssh_public_key": {
                "get_attr": [
                  "ssh_key",
                  "public_key"
                ]
              },
              "database_password": {
                "get_attr": [
                  "database_password",
                  "value"
                ]
              },
              "database_host": {
                "get_attr": [
                  "database_server",
                  "networks",
                  "private",
                  0
                ]
              }
            }
          }
        }
      },
      "wp_secure_auth": {
        "type": "OS::Heat::RandomString",
        "properties": {
          "length": 32,
          "sequence": "hexdigits"
        }
      },
      "mysql_root_password": {
        "type": "OS::Heat::RandomString",
        "properties": {
          "length": 16,
          "sequence": "lettersdigits"
        }
      },
      "mysql_debian_password": {
        "type": "OS::Heat::RandomString",
        "properties": {
          "length": 16,
          "sequence": "lettersdigits"
        }
      },
      "wp_auth": {
        "type": "OS::Heat::RandomString",
        "properties": {
          "length": 32,
          "sequence": "hexdigits"
        }
      },
      "ssh_key": {
        "type": "OS::Nova::KeyPair",
        "properties": {
          "name": {
            "get_param": "OS::stack_id"
          },
          "save_private_key": true
        }
      },
      "wp_master_server": {
        "type": "OS::Nova::Server",
        "properties": {
          "key_name": {
            "get_resource": "ssh_key"
          },
          "flavor": {
            "get_param": "wp_master_server_flavor"
          },
          "name": {
            "get_param": "wp_master_server_hostname"
          },
          "image": {
            "get_param": "image"
          },
          "metadata": {
            "rax-heat": {
              "get_param": "OS::stack_id"
            }
          }
        }
      },
      "database_server_firewall": {
        "depends_on": "wp_master_server_setup",
        "type": "OS::Heat::ChefSolo",
        "properties": {
          "username": "root",
          "node": {
            "run_list": [
              "recipe[rax-wordpress::memcached-firewall]"
            ],
            "rax": {
              "memcached": {
                "clients": [
                  {
                    "get_attr": [
                      "wp_master_server",
                      "networks",
                      "private",
                      0
                    ]
                  },
                  {
                    "get_attr": [
                      "wp_web_servers",
                      "privateIPv4"
                    ]
                  }
                ]
              }
            }
          },
          "private_key": {
            "get_attr": [
              "ssh_key",
              "private_key"
            ]
          },
          "host": {
            "get_attr": [
              "database_server",
              "accessIPv4"
            ]
          },
          "chef_version": {
            "get_param": "chef_version"
          },
          "kitchen": {
            "get_param": "kitchen"
          }
        }
      },
      "database_server_setup": {
        "depends_on": "database_server",
        "type": "OS::Heat::ChefSolo",
        "properties": {
          "username": "root",
          "node": {
            "rax": {
              "firewall": {
                "tcp": [
                  22
                ]
              },
              "mysql": {
                "innodb_buffer_pool_mempercent": 0.6
              }
            },
            "memcached": {
              "listen": {
                "get_attr": [
                  "database_server",
                  "networks",
                  "private",
                  0
                ]
              },
              "memory": 500
            },
            "hollandbackup": {
              "main": {
                "mysqldump": {
                  "host": "localhost",
                  "password": {
                    "get_attr": [
                      "mysql_root_password",
                      "value"
                    ]
                  },
                  "user": "root"
                },
                "backup_directory": "/var/lib/mysqlbackup"
              }
            },
            "run_list": [
              "recipe[apt]",
              "recipe[build-essential]",
              "recipe[rax-firewall]",
              "recipe[mysql::server]",
              "recipe[rax-wordpress::memcached-firewall]",
              "recipe[memcached]",
              "recipe[rax-wordpress::mysql]",
              "recipe[rax-wordpress::mysql-firewall]",
              "recipe[hollandbackup]",
              "recipe[hollandbackup::mysqldump]",
              "recipe[hollandbackup::main]",
              "recipe[hollandbackup::backupsets]",
              "recipe[hollandbackup::cron]"
            ],
            "mysql": {
              "remove_test_database": true,
              "root_network_acl": [
                "10.%"
              ],
              "server_debian_password": {
                "get_attr": [
                  "mysql_debian_password",
                  "value"
                ]
              },
              "server_root_password": {
                "get_attr": [
                  "mysql_root_password",
                  "value"
                ]
              },
              "bind_address": {
                "get_attr": [
                  "database_server",
                  "networks",
                  "private",
                  0
                ]
              },
              "remove_anonymous_users": true,
              "server_repl_password": {
                "get_attr": [
                  "mysql_repl_password",
                  "value"
                ]
              }
            }
          },
          "private_key": {
            "get_attr": [
              "ssh_key",
              "private_key"
            ]
          },
          "host": {
            "get_attr": [
              "database_server",
              "accessIPv4"
            ]
          },
          "chef_version": {
            "get_param": "chef_version"
          },
          "kitchen": {
            "get_param": "kitchen"
          }
        }
      },
      "wp_master_server_setup": {
        "depends_on": [
          "database_server_setup",
          "wp_web_servers"
        ],
        "type": "OS::Heat::ChefSolo",
        "properties": {
          "username": "root",
          "node": {
            "varnish": {
              "version": "3.0",
              "listen_port": "80"
            },
            "sysctl": {
              "values": {
                "fs.inotify.max_user_watches": 1000000
              }
            },
            "lsyncd": {
              "interval": 5
            },
            "monit": {
              "mail_format": {
                "from": "monit@localhost"
              },
              "notify_email": "root@localhost"
            },
            "vsftpd": {
              "chroot_local_user": false,
              "ssl_ciphers": "AES256-SHA",
              "write_enable": true,
              "local_umask": "002",
              "hide_ids": false,
              "ssl_enable": true,
              "ipaddress": ""
            },
            "wordpress": {
              "keys": {
                "logged_in": {
                  "get_attr": [
                    "wp_logged_in",
                    "value"
                  ]
                },
                "secure_auth_key": {
                  "get_attr": [
                    "wp_secure_auth",
                    "value"
                  ]
                },
                "nonce_key": {
                  "get_attr": [
                    "wp_nonce",
                    "value"
                  ]
                },
                "auth": {
                  "get_attr": [
                    "wp_auth",
                    "value"
                  ]
                }
              },
              "server_aliases": [
                {
                  "get_param": "domain"
                }
              ],
              "version": {
                "get_param": "version"
              },
              "db": {
                "host": {
                  "get_attr": [
                    "database_server",
                    "networks",
                    "private",
                    0
                  ]
                },
                "pass": {
                  "get_attr": [
                    "database_password",
                    "value"
                  ]
                },
                "user": {
                  "get_param": "username"
                },
                "name": {
                  "get_param": "database_name"
                }
              },
              "dir": {
                "str_replace": {
                  "params": {
                    "%domain%": {
                      "get_param": "domain"
                    }
                  },
                  "template": "/var/www/vhosts/%domain%"
                }
              }
            },
            "run_list": [
              "recipe[apt]",
              "recipe[build-essential]",
              "recipe[mysql::client]",
              "recipe[mysql-chef_gem]",
              "recipe[rax-wordpress::apache-prep]",
              "recipe[sysctl::attribute_driver]",
              "recipe[rax-wordpress::x509]",
              "recipe[php]",
              "recipe[rax-install-packages]",
              "recipe[rax-wordpress::wp-database]",
              "recipe[wordpress]",
              "recipe[rax-wordpress::wp-setup]",
              "recipe[rax-wordpress::user]",
              "recipe[rax-wordpress::memcache]",
              "recipe[lsyncd]",
              "recipe[vsftpd]",
              "recipe[rax-wordpress::vsftpd]",
              "recipe[varnish::repo]",
              "recipe[varnish]",
              "recipe[rax-wordpress::apache]",
              "recipe[rax-wordpress::varnish]",
              "recipe[rax-wordpress::varnish-firewall]",
              "recipe[rax-wordpress::firewall]",
              "recipe[rax-wordpress::vsftpd-firewall]",
              "recipe[rax-wordpress::lsyncd]"
            ],
            "mysql": {
              "server_root_password": {
                "get_attr": [
                  "mysql_root_password",
                  "value"
                ]
              },
              "bind_address": {
                "get_attr": [
                  "mysql_root_password",
                  "value"
                ]
              }
            },
            "apache": {
              "listen_ports": [
                8080
              ],
              "serversignature": "Off",
              "traceenable": "Off",
              "timeout": 30
            },
            "rax": {
              "varnish": {
                "master_backend": "localhost"
              },
              "lsyncd": {
                "clients": {
                  "get_attr": [
                    "wp_web_servers",
                    "privateIPv4"
                  ]
                },
                "ssh": {
                  "private_key": {
                    "get_attr": [
                      "sync_key",
                      "private_key"
                    ]
                  }
                }
              },
              "memcache": {
                "server": {
                  "get_attr": [
                    "database_server",
                    "networks",
                    "private",
                    0
                  ]
                }
              },
              "wordpress": {
                "admin_pass": {
                  "get_attr": [
                    "database_password",
                    "value"
                  ]
                },
                "admin_user": {
                  "get_param": "username"
                },
                "user": {
                  "group": {
                    "get_param": "username"
                  },
                  "name": {
                    "get_param": "username"
                  }
                }
              },
              "apache": {
                "domain": {
                  "get_param": "domain"
                }
              },
              "packages": [
                "php5-imagick"
              ]
            }
          },
          "private_key": {
            "get_attr": [
              "ssh_key",
              "private_key"
            ]
          },
          "host": {
            "get_attr": [
              "wp_master_server",
              "accessIPv4"
            ]
          },
          "chef_version": {
            "get_param": "chef_version"
          },
          "kitchen": {
            "get_param": "kitchen"
          }
        }
      },
      "wp_logged_in": {
        "type": "OS::Heat::RandomString",
        "properties": {
          "length": 32,
          "sequence": "hexdigits"
        }
      },
      "mysql_repl_password": {
        "type": "OS::Heat::RandomString",
        "properties": {
          "length": 16,
          "sequence": "lettersdigits"
        }
      },
      "database_password": {
        "type": "OS::Heat::RandomString",
        "properties": {
          "length": 16,
          "sequence": "lettersdigits"
        }
      },
      "wp_nonce": {
        "type": "OS::Heat::RandomString",
        "properties": {
          "length": 32,
          "sequence": "hexdigits"
        }
      }
    }
  },
  "action": "CREATE",
  "project_id": "883286",
  "id": "1b3f2124-6c96-4ae7-b33f-2c3e2360bce0",
  "resources": {
    "load_balancer": {
      "status": "COMPLETE",
      "name": "load_balancer",
      "resource_data": {},
      "resource_id": "374755",
      "action": "CREATE",
      "type": "Rackspace::Cloud::LoadBalancer",
      "metadata": {}
    },
    "sync_key": {
      "status": "COMPLETE",
      "name": "sync_key",
      "resource_data": {
        "private_key": "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEAtBkPznL4r8SBjdksN64J5Vm5HOfpN3+G35BFWp/7P1DBvQvl\nB44Gk/xn5Y/3OENC6GRqRJgp3fCXdxzs+o7iqKWqFCSycspN1CezGUojhP9ISr1L\n/q5sSujRRyl2fTA6x2Xnc2uVrg44mPijgIfblbgLCWBgwSONk0wqlsIBosApkYKy\nbtTM39zpmMKhx9vdWi5mEDpYJSJea40EW68nKbdW4DpL2nEJUAAZbQ+/GlEaviix\nQLUOP5B/PmPSNFiv/zm1NtbLFii1Ep5rxbgnii3PlNAmB3+fX75UbvukinYx0+kW\nnDSRbW5m9UbIMt4vznwEwysCOovybkZPN7ZlpwIDAQABAoIBAE2At3+llIW3b/VG\nLzQq7lFHwlTBLGjYtYcCBAaS8EF4FFexhbcxlH0c0u1EfiQ1NdbiV6T7QpEjF1uI\nFCdjVAE1gbK3dB/YFZQmHXnVoOF8JnUbb1fDYhD+jgksu7P2DGWA4hCWjMxhjFOw\nNFR8oq+UixNW6WxUS3nG/lDwXlnV1WHkPlrvHQRSNjDuuMR3SdwLM7N4iqUpq6pM\nrYSijCW7KqyYhno29/n7DmX11RncbN73LSq6Sn1RMQomNSv7ogahbzwBg7f2GjKB\nRqhTpYNNEXgiCvM35okra9q/SnPKJackacP5ZMtVFOQtsenljpjyof85xMuan/fd\nPwDANWkCgYEA3mD1HRqZOfWa5oG2Wvr83AdBa+rkvXum8r3kbwVQLDeV0KiRktTs\nF1lhtij44LFawF5f4I6UTqdXnNkaLceYabA/sFyb5+3TGDv04ajvHC8z2pshWSEX\negx9tnQI0Ucjnmch4/8gn+gbxo+PfAOgMvG2zn/AluJCClUMYev3lv0CgYEAz1Ol\n+Jpk3/mrKj9ClARbzXRkZ/spBEIOK7sW5fvvj7v5dFsfDOxO7Qj0PCvFEy/O9ght\nLmPVj64xCd5fjSZHVPvToiK0FiqPV1t22g6/3B5vsDcAsVlL336tahXTCR3K6ALk\nzH5HLSjUKb+1qbMzMyElSwPHVPB4fnJC14B9enMCgYBPq/0liDoNgekVXLOwtOuT\nCSZvO6DoIj0WCuKkxAqNTPzn3P0K1i4fz24qjVNdbS1OboF7Opn39Ax3rXCrpi78\n7qBi10skNRjEPfbmQlgoiODTGXFBNZHrsD35+GiQUiR4xApoXSebItWQti56B/KF\nTgRox2yAol92xDHDg38ZIQKBgQDGTr5sIlHmoksEZ+no5ppg1LnNc8Fx3zTqw1NN\nvEMSerxKfXYfyFBeDbh/bWZdydbuInU8cCWv/u/M/rTqr/h+4zk01njm0uK0rjnq\nrTz68Onn5VR2TnFyXxrEZAetqp+QeGQc7ZRrL6hwHn1Gyq9ocoXXUM/zAOhgGi6x\nLqfW3QKBgQCHLIuNjIBFYbDDcYpmZ8L6GZPUrMLPM/+KgDmDO9yXgoG7MUA7wHtw\n36IRPJwVpllqFapAUj1Ryje995eKajmBAYS3AmFrixQK+Me8v15L1usPxw4vCMoW\nu92e1fSDR7YkZ0wWORTc3IVUY/x8994latJIbAteh7xb1LXcFcW14g==\n-----END RSA PRIVATE KEY-----\n"
      },
      "resource_id": "1b3f2124-6c96-4ae7-b33f-2c3e2360bce0-sync",
      "action": "CREATE",
      "type": "OS::Nova::KeyPair",
      "metadata": {}
    },
    "database_server": {
      "status": "COMPLETE",
      "name": "database_server",
      "resource_data": {},
      "resource_id": "2fd46a4f-fa11-4b35-b8b4-23701fca1fde",
      "action": "CREATE",
      "type": "OS::Nova::Server",
      "metadata": {}
    },
    "wp_web_servers": {
      "status": "COMPLETE",
      "name": "blah-wp_web_servers-siiunxvwadjq",
      "stack_user_project_id": "883286",
      "environment": {
        "parameter_defaults": {},
        "parameters": {},
        "resource_registry": {
          "https://raw.githubusercontent.com/rackspace-orchestration-templates/wordpress-multi/master/wordpress-web-server.yaml": "https://raw.githubusercontent.com/rackspace-orchestration-templates/wordpress-multi/master/wordpress-web-server.yaml",
          "resources": {}
        }
      },
      "template": {
        "heat_template_version": "2013-05-23",
        "resources": {
          "0": {
            "type": "https://raw.githubusercontent.com/rackspace-orchestration-templates/wordpress-multi/master/wordpress-web-server.yaml",
            "properties": {
              "domain": "example.com",
              "image": "Ubuntu 12.04 LTS (Precise Pangolin) (PVHVM)",
              "wp_nonce": "31A1051C275393AC05EDEA20F403FDB0",
              "memcached_host": "10.210.32.93",
              "prefix": "wp_",
              "ssh_private_key": "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEAwodOJzsxx1PxB3GW2OmAgGptFAN59QzQ0AN22jfubpOGfH81\nlywG1anIRvJBQq9acj4QZrEnkAc0PBbBa7nWjnDW/Wf1pb7mtxZ31oRamw0Z8mM4\nHcYO2J5fF6jB+ndhmneObtm0oKTKZabL7Au0sVXdLLo3WKvIFMmt5/Z3sTg7zq6c\nWY+LiM2En1AGBoolyVKDb3pDKTz23PWycQZ4nmQqIF4nh0tnEe91klvIc8XhXlSS\nYzA2XBjUw2OtcjwROzVuP8AMKOwwZd7IANdGOiTvpDbMkjEKtwC9xngp4qp082WF\nGXZK45wfzWodrPhj4ib1vA0Axz9ud1+Cij2sEQIDAQABAoIBABx1lyV+L4Yt7bFd\nGOibIMWozFSFPa5wNYx5NUYvsJ5UzvQf2ENJmaZgtIBMqOeMp/rWwaeEe3lC1I2F\n9r4/7ffg4lMohnO9PhvDGb00l9zfSdCAW5FfjIR8hwT7F4YBOTJUE258Q0TNVx8Q\nC/14qPLY0QbeJ4K9fwQrjVnGYTR3+E4siLlkuZ6dyvY+xSfnj8UolCiAQsYbzO6U\nV7swBbpZUHOS08CdNe/GBguCjiiv6cAUGlWzJPUgxMJQCPdbKXvS/dEudbw43AJS\nHvJawdkbvh/ji9s8fOUJmOMlIm1adh5g5dT71l1ptkCx4tsB2dz5O92oVF9QUlvr\nETY+hFECgYEA6HTFrR/KULzjjISnWGK+LvZaI/Iszo3Eo+1vjrGc26WAQzchRBpC\nUPx3rLoPviCcE4XF5frx+XDJ4lenC64jvumwphT7AiQ3z5v5KyG2eN8GZchFDC+Q\niAVvuTM9CZETW6DaLEMYmDgrEmgbU1JnkPFDz7FYBCen8rtjuyrI+G8CgYEA1jsh\nCLMOhVxSzgYbZcx3683w9/ilQ7yCY4htg49b6xYt1vliSVQEvwP0KH81rK5sD9lB\nZHuI0gFDXLYnxY9waMYGZLtDTkyDB7081a00+2Pw9I/2/dPuyqLeSjBjBwwlekZJ\n33ZO3r6p4QJoOIw1fJIt/jwmdhCRWd9L2UfA438CgYEAlH/8xJN5gMiaqWsZKQqz\nqnawsSQF4dKJW5vUV5k5tsvsu4PdmY8Y7HnMzihy5Cga7RHZkgkVSh/2qMUMLxcJ\nOO47bm4ayIxwpw1iSV6ZHnCDusQM8DL2px6p9+s2xATNFA0XM42NibjgMzsUsc8D\n4IFwq58EtmrLDPMPTEOR7bsCgYBvYTSOilF9Yn+mn6Q06/ZZQawLsFlz+xkrWG3f\nnXQjqFdS0juYdjc1fH+/YkvsqI6EOub1sAh1brSwCgBphWbjAjmmu3mFxt/E8U0k\nprXKEa7f5815MGuRLNY3airCKj198fdMV/0vb59w3ciDxdm1F2cUK/+vGHQJbr/H\niretTwKBgQDX3KrSleLIgTLLJCWXgyyFMFj33BCA4STUl4KdSTaGoc614p7tclS5\n+ObQno5dXtjHEYYKh8lxlZszyd4qm3hdn6rQpKG4qRlnTKV2L3kW1kMY9E0Jh21z\nt7Uur7XAOzOw7TGidiaWrMBX1NqJdN0ndE+IjZVDyWrayMvlRntVEg==\n-----END RSA PRIVATE KEY-----\n",
              "lsync_pub": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC0GQ/OcvivxIGN2Sw3rgnlWbkc5+k3f4bfkEVan/s/UMG9C+UHjgaT/Gflj/c4Q0LoZGpEmCnd8Jd3HOz6juKopaoUJLJyyk3UJ7MZSiOE/0hKvUv+rmxK6NFHKXZ9MDrHZedza5WuDjiY+KOAh9uVuAsJYGDBI42TTCqWwgGiwCmRgrJu1Mzf3OmYwqHH291aLmYQOlglIl5rjQRbrycpt1bgOkvacQlQABltD78aURq+KLFAtQ4/kH8+Y9I0WK//ObU21ssWKLUSnmvFuCeKLc+U0CYHf59fvlRu+6SKdjHT6RacNJFtbmb1Rsgy3i/OfATDKwI6i/JuRk83tmWn Generated-by-Nova\n",
              "wp_auth": "757ED40CF7D92DF36B09278F8F06DD84",
              "version": "3.9.2",
              "chef_version": "11.16.2",
              "username": "wp_user",
              "wp_web_server_flavor": "2 GB General Purpose v1",
              "varnish_master_backend": "10.210.2.148",
              "parent_stack_id": "1b3f2124-6c96-4ae7-b33f-2c3e2360bce0",
              "wp_logged_in": "4FF09E766606919DA25514A1E33C6177",
              "kitchen": "https://github.com/rackspace-orchestration-templates/wordpress-multi",
              "wp_secure_auth": "EFEE2A602360DA441B609976CD3D8138",
              "ssh_keypair_name": "1b3f2124-6c96-4ae7-b33f-2c3e2360bce0",
              "database_name": "wordpress",
              "wp_web_server_hostname": "WordPress-Web0",
              "ssh_public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDCh04nOzHHU/EHcZbY6YCAam0UA3n1DNDQA3baN+5uk4Z8fzWXLAbVqchG8kFCr1pyPhBmsSeQBzQ8FsFrudaOcNb9Z/Wlvua3FnfWhFqbDRnyYzgdxg7Ynl8XqMH6d2Gad45u2bSgpMplpsvsC7SxVd0sujdYq8gUya3n9nexODvOrpxZj4uIzYSfUAYGiiXJUoNvekMpPPbc9bJxBnieZCogXieHS2cR73WSW8hzxeFeVJJjMDZcGNTDY61yPBE7NW4/wAwo7DBl3sgA10Y6JO+kNsySMQq3AL3GeCniqnTzZYUZdkrjnB/Nah2s+GPiJvW8DQDHP253X4KKPawR Generated-by-Nova\n",
              "database_password": "YVJ237mOBT3nxEtL",
              "database_host": "10.210.32.93"
            }
          }
        }
      },
      "action": "CREATE",
      "project_id": "883286",
      "id": "61bad1a5-2e7b-45fc-9baf-6e1140306233",
      "resources": {
        "0": {
          "status": "COMPLETE",
          "name": "blah-wp_web_servers-siiunxvwadjq-0-t3di232y7j3e",
          "stack_user_project_id": "883286",
          "environment": {
            "parameter_defaults": {},
            "parameters": {
              "domain": "example.com",
              "image": "Ubuntu 12.04 LTS (Precise Pangolin) (PVHVM)",
              "wp_nonce": "31A1051C275393AC05EDEA20F403FDB0",
              "parent_stack_id": "1b3f2124-6c96-4ae7-b33f-2c3e2360bce0",
              "prefix": "wp_",
              "ssh_private_key": "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEAwodOJzsxx1PxB3GW2OmAgGptFAN59QzQ0AN22jfubpOGfH81\nlywG1anIRvJBQq9acj4QZrEnkAc0PBbBa7nWjnDW/Wf1pb7mtxZ31oRamw0Z8mM4\nHcYO2J5fF6jB+ndhmneObtm0oKTKZabL7Au0sVXdLLo3WKvIFMmt5/Z3sTg7zq6c\nWY+LiM2En1AGBoolyVKDb3pDKTz23PWycQZ4nmQqIF4nh0tnEe91klvIc8XhXlSS\nYzA2XBjUw2OtcjwROzVuP8AMKOwwZd7IANdGOiTvpDbMkjEKtwC9xngp4qp082WF\nGXZK45wfzWodrPhj4ib1vA0Axz9ud1+Cij2sEQIDAQABAoIBABx1lyV+L4Yt7bFd\nGOibIMWozFSFPa5wNYx5NUYvsJ5UzvQf2ENJmaZgtIBMqOeMp/rWwaeEe3lC1I2F\n9r4/7ffg4lMohnO9PhvDGb00l9zfSdCAW5FfjIR8hwT7F4YBOTJUE258Q0TNVx8Q\nC/14qPLY0QbeJ4K9fwQrjVnGYTR3+E4siLlkuZ6dyvY+xSfnj8UolCiAQsYbzO6U\nV7swBbpZUHOS08CdNe/GBguCjiiv6cAUGlWzJPUgxMJQCPdbKXvS/dEudbw43AJS\nHvJawdkbvh/ji9s8fOUJmOMlIm1adh5g5dT71l1ptkCx4tsB2dz5O92oVF9QUlvr\nETY+hFECgYEA6HTFrR/KULzjjISnWGK+LvZaI/Iszo3Eo+1vjrGc26WAQzchRBpC\nUPx3rLoPviCcE4XF5frx+XDJ4lenC64jvumwphT7AiQ3z5v5KyG2eN8GZchFDC+Q\niAVvuTM9CZETW6DaLEMYmDgrEmgbU1JnkPFDz7FYBCen8rtjuyrI+G8CgYEA1jsh\nCLMOhVxSzgYbZcx3683w9/ilQ7yCY4htg49b6xYt1vliSVQEvwP0KH81rK5sD9lB\nZHuI0gFDXLYnxY9waMYGZLtDTkyDB7081a00+2Pw9I/2/dPuyqLeSjBjBwwlekZJ\n33ZO3r6p4QJoOIw1fJIt/jwmdhCRWd9L2UfA438CgYEAlH/8xJN5gMiaqWsZKQqz\nqnawsSQF4dKJW5vUV5k5tsvsu4PdmY8Y7HnMzihy5Cga7RHZkgkVSh/2qMUMLxcJ\nOO47bm4ayIxwpw1iSV6ZHnCDusQM8DL2px6p9+s2xATNFA0XM42NibjgMzsUsc8D\n4IFwq58EtmrLDPMPTEOR7bsCgYBvYTSOilF9Yn+mn6Q06/ZZQawLsFlz+xkrWG3f\nnXQjqFdS0juYdjc1fH+/YkvsqI6EOub1sAh1brSwCgBphWbjAjmmu3mFxt/E8U0k\nprXKEa7f5815MGuRLNY3airCKj198fdMV/0vb59w3ciDxdm1F2cUK/+vGHQJbr/H\niretTwKBgQDX3KrSleLIgTLLJCWXgyyFMFj33BCA4STUl4KdSTaGoc614p7tclS5\n+ObQno5dXtjHEYYKh8lxlZszyd4qm3hdn6rQpKG4qRlnTKV2L3kW1kMY9E0Jh21z\nt7Uur7XAOzOw7TGidiaWrMBX1NqJdN0ndE+IjZVDyWrayMvlRntVEg==\n-----END RSA PRIVATE KEY-----\n",
              "lsync_pub": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC0GQ/OcvivxIGN2Sw3rgnlWbkc5+k3f4bfkEVan/s/UMG9C+UHjgaT/Gflj/c4Q0LoZGpEmCnd8Jd3HOz6juKopaoUJLJyyk3UJ7MZSiOE/0hKvUv+rmxK6NFHKXZ9MDrHZedza5WuDjiY+KOAh9uVuAsJYGDBI42TTCqWwgGiwCmRgrJu1Mzf3OmYwqHH291aLmYQOlglIl5rjQRbrycpt1bgOkvacQlQABltD78aURq+KLFAtQ4/kH8+Y9I0WK//ObU21ssWKLUSnmvFuCeKLc+U0CYHf59fvlRu+6SKdjHT6RacNJFtbmb1Rsgy3i/OfATDKwI6i/JuRk83tmWn Generated-by-Nova\n",
              "wp_auth": "757ED40CF7D92DF36B09278F8F06DD84",
              "version": "3.9.2",
              "chef_version": "11.16.2",
              "username": "wp_user",
              "wp_web_server_flavor": "2 GB General Purpose v1",
              "varnish_master_backend": "10.210.2.148",
              "memcached_host": "10.210.32.93",
              "wp_logged_in": "4FF09E766606919DA25514A1E33C6177",
              "kitchen": "https://github.com/rackspace-orchestration-templates/wordpress-multi",
              "wp_secure_auth": "EFEE2A602360DA441B609976CD3D8138",
              "ssh_keypair_name": "1b3f2124-6c96-4ae7-b33f-2c3e2360bce0",
              "database_name": "wordpress",
              "wp_web_server_hostname": "WordPress-Web0",
              "ssh_public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDCh04nOzHHU/EHcZbY6YCAam0UA3n1DNDQA3baN+5uk4Z8fzWXLAbVqchG8kFCr1pyPhBmsSeQBzQ8FsFrudaOcNb9Z/Wlvua3FnfWhFqbDRnyYzgdxg7Ynl8XqMH6d2Gad45u2bSgpMplpsvsC7SxVd0sujdYq8gUya3n9nexODvOrpxZj4uIzYSfUAYGiiXJUoNvekMpPPbc9bJxBnieZCogXieHS2cR73WSW8hzxeFeVJJjMDZcGNTDY61yPBE7NW4/wAwo7DBl3sgA10Y6JO+kNsySMQq3AL3GeCniqnTzZYUZdkrjnB/Nah2s+GPiJvW8DQDHP253X4KKPawR Generated-by-Nova\n",
              "database_password": "YVJ237mOBT3nxEtL",
              "database_host": "10.210.32.93"
            },
            "resource_registry": {
              "resources": {}
            }
          },
          "template": {
            "outputs": {
              "accessIPv4": {
                "value": {
                  "get_attr": [
                    "wp_web_server",
                    "accessIPv4"
                  ]
                }
              },
              "privateIPv4": {
                "value": {
                  "get_attr": [
                    "wp_web_server",
                    "networks",
                    "private",
                    0
                  ]
                }
              }
            },
            "heat_template_version": "2013-05-23",
            "description": "This is a Heat template to deploy a single Linux server running a WordPress.\n",
            "parameters": {
              "domain": {
                "default": "example.com",
                "type": "string",
                "description": "Domain to be used with WordPress site"
              },
              "image": {
                "default": "Ubuntu 12.04 LTS (Precise Pangolin) (PVHVM)",
                "type": "string",
                "description": "Server Image used for all servers.",
                "constraints": [
                  {
                    "description": "Must be a supported operating system.",
                    "allowed_values": [
                      "Ubuntu 12.04 LTS (Precise Pangolin) (PVHVM)"
                    ]
                  }
                ]
              },
              "wp_auth": {
                "type": "string"
              },
              "memcached_host": {
                "default": "127.0.0.1",
                "type": "string",
                "description": "IP/Host of the memcached server"
              },
              "prefix": {
                "default": "wp_",
                "type": "string",
                "description": "Prefix to use for"
              },
              "ssh_private_key": {
                "type": "string"
              },
              "lsync_pub": {
                "type": "string",
                "description": "Public key for lsync configuration",
                "constraints": null
              },
              "wp_nonce": {
                "type": "string"
              },
              "version": {
                "default": "3.9.1",
                "type": "string",
                "description": "Version of WordPress to install"
              },
              "chef_version": {
                "default": "11.16.2",
                "type": "string",
                "description": "Version of chef client to use"
              },
              "username": {
                "default": "wp_user",
                "type": "string",
                "description": "Username for system, database, and WordPress logins."
              },
              "wp_web_server_flavor": {
                "default": "2 GB General Purpose v1",
                "type": "string",
                "description": "Web Cloud Server flavor",
                "constraints": [
                  {
                    "description": "Must be a valid Rackspace Cloud Server flavor for the region you have\nselected to deploy into.\n",
                    "allowed_values": [
                      "1 GB General Purpose v1",
                      "2 GB General Purpose v1",
                      "4 GB General Purpose v1",
                      "8 GB General Purpose v1",
                      "15 GB I/O v1",
                      "30 GB I/O v1",
                      "1GB Standard Instance",
                      "2GB Standard Instance",
                      "4GB Standard Instance",
                      "8GB Standard Instance",
                      "15GB Standard Instance",
                      "30GB Standard Instance"
                    ]
                  }
                ]
              },
              "varnish_master_backend": {
                "default": "localhost",
                "type": "string",
                "description": "Master backend host for admin calls in Varnish"
              },
              "parent_stack_id": {
                "default": "none",
                "type": "string",
                "description": "Stack id of the parent stack"
              },
              "wp_logged_in": {
                "type": "string"
              },
              "kitchen": {
                "default": "https://github.com/rackspace-orchestration-templates/wordpress-multi",
                "type": "string",
                "description": "URL for the kitchen to use"
              },
              "wp_secure_auth": {
                "type": "string"
              },
              "ssh_keypair_name": {
                "type": "string",
                "description": "keypair name to register with Nova for the root SSH key"
              },
              "database_name": {
                "default": "wordpress",
                "type": "string",
                "description": "WordPress database name"
              },
              "wp_web_server_hostname": {
                "default": "WordPress-Web",
                "type": "string",
                "description": "WordPress Web Server Name",
                "constraints": [
                  {
                    "length": {
                      "max": 64,
                      "min": 1
                    }
                  },
                  {
                    "allowed_pattern": "^[a-zA-Z][a-zA-Z0-9-]*$",
                    "description": "Must begin with a letter and contain only alphanumeric characters.\n"
                  }
                ]
              },
              "ssh_public_key": {
                "type": "string"
              },
              "database_password": {
                "type": "string",
                "description": "Password to use for database connections."
              },
              "database_host": {
                "default": "127.0.0.1",
                "type": "string",
                "description": "IP/Host of the database server"
              }
            },
            "resources": {
              "wp_web_server_setup": {
                "depends_on": "wp_web_server",
                "type": "OS::Heat::ChefSolo",
                "properties": {
                  "username": "root",
                  "node": {
                    "apache": {
                      "listen_ports": [
                        8080
                      ],
                      "serversignature": "Off",
                      "traceenable": "Off",
                      "timeout": 30
                    },
                    "varnish": {
                      "version": "3.0",
                      "listen_port": "80"
                    },
                    "wordpress": {
                      "keys": {
                        "logged_in": {
                          "get_param": "wp_logged_in"
                        },
                        "secure_auth_key": {
                          "get_param": "wp_secure_auth"
                        },
                        "nonce_key": {
                          "get_param": "wp_nonce"
                        },
                        "auth": {
                          "get_param": "wp_auth"
                        }
                      },
                      "server_aliases": [
                        {
                          "get_param": "domain"
                        }
                      ],
                      "version": {
                        "get_param": "version"
                      },
                      "db": {
                        "host": {
                          "get_param": "database_host"
                        },
                        "user": {
                          "get_param": "username"
                        },
                        "name": {
                          "get_param": "database_name"
                        },
                        "pass": {
                          "get_param": "database_password"
                        }
                      },
                      "dir": {
                        "str_replace": {
                          "params": {
                            "%domain%": {
                              "get_param": "domain"
                            }
                          },
                          "template": "/var/www/vhosts/%domain%"
                        }
                      }
                    },
                    "rax": {
                      "varnish": {
                        "master_backend": {
                          "get_param": "varnish_master_backend"
                        }
                      },
                      "lsyncd": {
                        "ssh": {
                          "pub": {
                            "get_param": "lsync_pub"
                          }
                        }
                      },
                      "memcache": {
                        "server": {
                          "get_param": "memcached_host"
                        }
                      },
                      "wordpress": {
                        "admin_pass": {
                          "get_param": "database_password"
                        },
                        "user": {
                          "group": {
                            "get_param": "username"
                          },
                          "name": {
                            "get_param": "username"
                          }
                        }
                      },
                      "apache": {
                        "domain": {
                          "get_param": "domain"
                        }
                      },
                      "packages": [
                        "php5-imagick"
                      ]
                    },
                    "run_list": [
                      "recipe[apt]",
                      "recipe[build-essential]",
                      "recipe[rax-wordpress::apache-prep]",
                      "recipe[rax-wordpress::x509]",
                      "recipe[php]",
                      "recipe[rax-install-packages]",
                      "recipe[wordpress]",
                      "recipe[rax-wordpress::user]",
                      "recipe[rax-wordpress::memcache]",
                      "recipe[varnish::repo]",
                      "recipe[varnish]",
                      "recipe[rax-wordpress::apache]",
                      "recipe[rax-wordpress::varnish]",
                      "recipe[rax-wordpress::firewall]",
                      "recipe[rax-wordpress::lsyncd-client]"
                    ]
                  },
                  "private_key": {
                    "get_param": "ssh_private_key"
                  },
                  "host": {
                    "get_attr": [
                      "wp_web_server",
                      "accessIPv4"
                    ]
                  },
                  "chef_version": {
                    "get_param": "chef_version"
                  },
                  "kitchen": {
                    "get_param": "kitchen"
                  }
                }
              },
              "wp_web_server": {
                "type": "OS::Nova::Server",
                "properties": {
                  "key_name": {
                    "get_param": "ssh_keypair_name"
                  },
                  "flavor": {
                    "get_param": "wp_web_server_flavor"
                  },
                  "name": {
                    "get_param": "wp_web_server_hostname"
                  },
                  "image": {
                    "get_param": "image"
                  },
                  "metadata": {
                    "rax-heat": {
                      "get_param": "parent_stack_id"
                    }
                  }
                }
              }
            }
          },
          "action": "CREATE",
          "project_id": "883286",
          "id": "6ff014e9-019d-4af0-9403-dbea8c58b9f5",
          "resources": {
            "wp_web_server_setup": {
              "status": "COMPLETE",
              "name": "wp_web_server_setup",
              "resource_data": {
                "process_id": "22766"
              },
              "resource_id": "4ac2da90-488b-4aa3-9d99-7e7778c394be",
              "action": "CREATE",
              "type": "OS::Heat::ChefSolo",
              "metadata": {}
            },
            "wp_web_server": {
              "status": "COMPLETE",
              "name": "wp_web_server",
              "resource_data": {},
              "resource_id": "14c3c5e7-a93c-4251-9813-96c1924b9d1a",
              "action": "CREATE",
              "type": "OS::Nova::Server",
              "metadata": {}
            }
          }
        }
      }
    },
    "wp_secure_auth": {
      "status": "COMPLETE",
      "name": "wp_secure_auth",
      "resource_data": {
        "value": "EFEE2A602360DA441B609976CD3D8138"
      },
      "resource_id": "blah-wp_secure_auth-ifyxgu5r5deq",
      "action": "CREATE",
      "type": "OS::Heat::RandomString",
      "metadata": {}
    },
    "mysql_root_password": {
      "status": "COMPLETE",
      "name": "mysql_root_password",
      "resource_data": {
        "value": "25Rj46CfmQ20zaiq"
      },
      "resource_id": "blah-mysql_root_password-ah3thb4rzwum",
      "action": "CREATE",
      "type": "OS::Heat::RandomString",
      "metadata": {}
    },
    "mysql_debian_password": {
      "status": "COMPLETE",
      "name": "mysql_debian_password",
      "resource_data": {
        "value": "HcACaHeHkzHjDVyc"
      },
      "resource_id": "blah-mysql_debian_password-vpvzonkhrrbn",
      "action": "CREATE",
      "type": "OS::Heat::RandomString",
      "metadata": {}
    },
    "wp_auth": {
      "status": "COMPLETE",
      "name": "wp_auth",
      "resource_data": {
        "value": "757ED40CF7D92DF36B09278F8F06DD84"
      },
      "resource_id": "blah-wp_auth-zy26zwn27v3q",
      "action": "CREATE",
      "type": "OS::Heat::RandomString",
      "metadata": {}
    },
    "ssh_key": {
      "status": "COMPLETE",
      "name": "ssh_key",
      "resource_data": {
        "private_key": "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEAwodOJzsxx1PxB3GW2OmAgGptFAN59QzQ0AN22jfubpOGfH81\nlywG1anIRvJBQq9acj4QZrEnkAc0PBbBa7nWjnDW/Wf1pb7mtxZ31oRamw0Z8mM4\nHcYO2J5fF6jB+ndhmneObtm0oKTKZabL7Au0sVXdLLo3WKvIFMmt5/Z3sTg7zq6c\nWY+LiM2En1AGBoolyVKDb3pDKTz23PWycQZ4nmQqIF4nh0tnEe91klvIc8XhXlSS\nYzA2XBjUw2OtcjwROzVuP8AMKOwwZd7IANdGOiTvpDbMkjEKtwC9xngp4qp082WF\nGXZK45wfzWodrPhj4ib1vA0Axz9ud1+Cij2sEQIDAQABAoIBABx1lyV+L4Yt7bFd\nGOibIMWozFSFPa5wNYx5NUYvsJ5UzvQf2ENJmaZgtIBMqOeMp/rWwaeEe3lC1I2F\n9r4/7ffg4lMohnO9PhvDGb00l9zfSdCAW5FfjIR8hwT7F4YBOTJUE258Q0TNVx8Q\nC/14qPLY0QbeJ4K9fwQrjVnGYTR3+E4siLlkuZ6dyvY+xSfnj8UolCiAQsYbzO6U\nV7swBbpZUHOS08CdNe/GBguCjiiv6cAUGlWzJPUgxMJQCPdbKXvS/dEudbw43AJS\nHvJawdkbvh/ji9s8fOUJmOMlIm1adh5g5dT71l1ptkCx4tsB2dz5O92oVF9QUlvr\nETY+hFECgYEA6HTFrR/KULzjjISnWGK+LvZaI/Iszo3Eo+1vjrGc26WAQzchRBpC\nUPx3rLoPviCcE4XF5frx+XDJ4lenC64jvumwphT7AiQ3z5v5KyG2eN8GZchFDC+Q\niAVvuTM9CZETW6DaLEMYmDgrEmgbU1JnkPFDz7FYBCen8rtjuyrI+G8CgYEA1jsh\nCLMOhVxSzgYbZcx3683w9/ilQ7yCY4htg49b6xYt1vliSVQEvwP0KH81rK5sD9lB\nZHuI0gFDXLYnxY9waMYGZLtDTkyDB7081a00+2Pw9I/2/dPuyqLeSjBjBwwlekZJ\n33ZO3r6p4QJoOIw1fJIt/jwmdhCRWd9L2UfA438CgYEAlH/8xJN5gMiaqWsZKQqz\nqnawsSQF4dKJW5vUV5k5tsvsu4PdmY8Y7HnMzihy5Cga7RHZkgkVSh/2qMUMLxcJ\nOO47bm4ayIxwpw1iSV6ZHnCDusQM8DL2px6p9+s2xATNFA0XM42NibjgMzsUsc8D\n4IFwq58EtmrLDPMPTEOR7bsCgYBvYTSOilF9Yn+mn6Q06/ZZQawLsFlz+xkrWG3f\nnXQjqFdS0juYdjc1fH+/YkvsqI6EOub1sAh1brSwCgBphWbjAjmmu3mFxt/E8U0k\nprXKEa7f5815MGuRLNY3airCKj198fdMV/0vb59w3ciDxdm1F2cUK/+vGHQJbr/H\niretTwKBgQDX3KrSleLIgTLLJCWXgyyFMFj33BCA4STUl4KdSTaGoc614p7tclS5\n+ObQno5dXtjHEYYKh8lxlZszyd4qm3hdn6rQpKG4qRlnTKV2L3kW1kMY9E0Jh21z\nt7Uur7XAOzOw7TGidiaWrMBX1NqJdN0ndE+IjZVDyWrayMvlRntVEg==\n-----END RSA PRIVATE KEY-----\n"
      },
      "resource_id": "1b3f2124-6c96-4ae7-b33f-2c3e2360bce0",
      "action": "CREATE",
      "type": "OS::Nova::KeyPair",
      "metadata": {}
    },
    "wp_master_server": {
      "status": "COMPLETE",
      "name": "wp_master_server",
      "resource_data": {},
      "resource_id": "29481dbb-70bd-4fa3-aec5-561e9f505023",
      "action": "CREATE",
      "type": "OS::Nova::Server",
      "metadata": {}
    },
    "database_server_firewall": {
      "status": "COMPLETE",
      "name": "database_server_firewall",
      "resource_data": {
        "process_id": "26582"
      },
      "resource_id": "12c3fcf7-9754-46b3-974a-c1f91b03eb16",
      "action": "CREATE",
      "type": "OS::Heat::ChefSolo",
      "metadata": {}
    },
    "database_server_setup": {
      "status": "COMPLETE",
      "name": "database_server_setup",
      "resource_data": {
        "process_id": "23271"
      },
      "resource_id": "8f97c16b-fba7-4ef6-9bfc-ffd763cc0ed7",
      "action": "CREATE",
      "type": "OS::Heat::ChefSolo",
      "metadata": {}
    },
    "wp_master_server_setup": {
      "status": "COMPLETE",
      "name": "wp_master_server_setup",
      "resource_data": {
        "process_id": "26327"
      },
      "resource_id": "2a91c4d4-99ac-41d5-b81e-46c13f103793",
      "action": "CREATE",
      "type": "OS::Heat::ChefSolo",
      "metadata": {}
    },
    "wp_logged_in": {
      "status": "COMPLETE",
      "name": "wp_logged_in",
      "resource_data": {
        "value": "4FF09E766606919DA25514A1E33C6177"
      },
      "resource_id": "blah-wp_logged_in-mayy4au5cwxb",
      "action": "CREATE",
      "type": "OS::Heat::RandomString",
      "metadata": {}
    },
    "mysql_repl_password": {
      "status": "COMPLETE",
      "name": "mysql_repl_password",
      "resource_data": {
        "value": "ltUIttHiPdYxmbXi"
      },
      "resource_id": "blah-mysql_repl_password-lm2s7cnqlz67",
      "action": "CREATE",
      "type": "OS::Heat::RandomString",
      "metadata": {}
    },
    "database_password": {
      "status": "COMPLETE",
      "name": "database_password",
      "resource_data": {
        "value": "YVJ237mOBT3nxEtL"
      },
      "resource_id": "blah-database_password-ebafl565k3ec",
      "action": "CREATE",
      "type": "OS::Heat::RandomString",
      "metadata": {}
    },
    "wp_nonce": {
      "status": "COMPLETE",
      "name": "wp_nonce",
      "resource_data": {
        "value": "31A1051C275393AC05EDEA20F403FDB0"
      },
      "resource_id": "blah-wp_nonce-ggd6lc7djfoy",
      "action": "CREATE",
      "type": "OS::Heat::RandomString",
      "metadata": {}
    }
  }
}
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
            create_stack_name = "CREATE_%s" % datetime.datetime.now().\
                microsecond
            try:
                csresp, csbody, stack_identifier = self.create_stack(
                    create_stack_name, region, yaml_template, parameters)
                self._check_resp(csresp, csbody, apiname)
            except BadStatusLine:
                print "Create stack did not work"

            #stack-list - doing this again because it has known to fail if
            # called after a stack create
            apiname = "stack list"
            slresp, stacklist = self.orchestration_client.list_stacks(region)
            self._check_resp(slresp, stacklist, apiname)

            #update stack
            apiname = "update stack"
            parameters_update = {
                    'username': 'sabeen'
            }

            updateStackName, updateStackId = self._get_stacks("UPDATE_",
                                                              stacklist,
                                                              region)
            if updateStackName != 0:
                try:
                    ssresp, ssbody = self.update_stack(updateStackId,
                                                       updateStackName, region,
                                                       yaml_template, parameters_update)
                    self._check_resp(ssresp, ssbody, apiname)
                except BadStatusLine:
                    print "Update stack did not work"

            #stack show
            apiname = "show stack"
            if updateStackName != 0:
                ssresp, ssbody = self.orchestration_client.show_stack(
                    updateStackName, updateStackId, region)
                self._check_resp(ssresp, ssbody, apiname)

            #stack preview
            apiname = "preview stack"
            if updateStackName != 0:
                spresp, spbody = self.orchestration_client.stack_preview(
                    name='preview_stack', region=region,
                    template=yaml_template)
                self._check_resp(spresp, spbody, apiname)

            #delete stack
            apiname = "delete stack"
            deleteStackName, deleteStackId = self._get_stacks("CREATE_",
                                                              stacklist,
                                                              region)
            if deleteStackName != 0:
                try:
                    ssresp, ssbody = self.orchestration_client.delete_stack(
                        deleteStackName, deleteStackId, region)
                    self._check_resp(ssresp, ssbody, apiname)
                except BadStatusLine:
                    print "Delete stack did not work"

            #abandon stack
            apiname = "abandon stack"
            abandonStackName, abandonStackId = self._get_stacks("ADOPT_",
                                                                stacklist,
                                                                region)
            if abandonStackName != 0:
                try:
                    abandonStackName = 'CREATE_504933'
                    abandonStackId = 'bf663682-d1d8-4b0e-9297-06ce130fec96'
                    asresp, asbody, = self.abandon_stack(abandonStackId,
                                                         abandonStackName, region)
                    self._check_resp(asresp, asbody, apiname)
                except BadStatusLine:
                    print "Delete stack did not work"

            apiname = "adopt stack"
            ipdb.set_trace()
            adopt_stack_name = "ADOPT_%s" %datetime.datetime.now().microsecond
            try:
                adresp, adbody, stack_identifier = self.adopt_stack(
                    adopt_stack_name, region, asbody, yaml_template,
                    parameters)
                self._check_resp(adresp, adbody, apiname)
            except BadStatusLine:
                print "Adopt stack did not work"

            #--------  Stack resources  --------
            #Lists resources in a stack
            apiname = "list resources"
            if updateStackName != 0:
                lrresp, lrbody = self.orchestration_client.list_resources(
                    updateStackName, updateStackId, region)
                self._check_resp(lrresp, lrbody, apiname)

            #Gets metadata for a specified resource.
            apiname = "resource metadata"
            if updateStackName != 0:
                rs_name = self._get_resource_name(lrbody)
                rmresp, rmbody = self.orchestration_client.\
                    show_resource_metadata(updateStackName, updateStackId,
                                           rs_name, region)
                self._check_resp(rmresp, rmbody, apiname)

            #Gets data for a specified resource.
            apiname = "get resources"
            if updateStackName != 0:
                rsresp, rsbody = self.orchestration_client.get_resource(
                    updateStackName, updateStackId, rs_name, region)
                self._check_resp(rsresp, rsbody, apiname)

            #Gets a template representation for a specified resource type.
            apiname = "resource template"
            if updateStackName != 0:
                rs_type = self._get_resource_type(lrbody)
                rtresp, rtbody = self.orchestration_client.resource_template(
                    rs_type, region)
                self._check_resp(rtresp, rtbody, apiname)

            #Lists the supported template resource types.
            apiname = "template resource types"
            rtresp, rtbody = self.orchestration_client.template_resource(
                region)
            self._check_resp(rtresp, rtbody, apiname)

            #Gets the interface schema for a specified resource type.
            apiname = "schema for resource type"
            if updateStackName != 0:
                rtresp, rtbody = self.orchestration_client.resource_schema(
                    rs_type, region)
                self._check_resp(rtresp, rtbody, apiname)


            #-------  Stack events  ----------
            #event list
            apiname = "list event"
            if updateStackName != 0:
                evresp, evbody = self.orchestration_client.list_events(
                    updateStackName, updateStackId, region)
                self._check_resp(evresp, evbody, apiname)

            #event show
            apiname = "show event"
            if updateStackName != 0:
                event_id, rs_name_event = self._get_event_id(evbody)
                esresp, esbody = self.orchestration_client.show_event(
                    updateStackName, updateStackId, rs_name_event, event_id,
                    region)
                self._check_resp(esresp, esbody, apiname)


            #-------  Templates  -------------
            #template show
            apiname = "template show"
            if updateStackName != 0:
                tsresp, tsbody = self.orchestration_client.show_template(
                    updateStackName, updateStackId, region)
                self._check_resp(tsresp, tsbody, apiname)

            #template validate
            apiname = "template validate"
            tvresp, tvbody = self.orchestration_client.validate_template(
                region, yaml_template, parameters)
            self._check_resp(tvresp, tvbody, apiname)


            #--------- Fusion -----------------
            # Get template catalog
            apiname = "fusion template catalog"
            tcresp, tcbody = self.orchestration_client.get_template_catalog(region)
            self._check_resp(tcresp, tcbody, apiname)

            # Get single template from catalog
            apiname = "fusion single template"
            template_id = "wordpress-single"
            tsresp, tsbody = self.orchestration_client.get_single_template(template_id, region)
            self._check_resp(tsresp, tsbody, apiname)

            # Get template catalog with metadata
            apiname = "fusion template catalog metadata"
            cmresp, cmbody = self.orchestration_client.get_template_catalog_with_metadata(region)
            self._check_resp(cmresp, cmbody, apiname)

            # Get single template catalog with metadata
            apiname = "fusion single catalog metadata"
            template_id = "wordpress-single"
            smresp, smbody = self.orchestration_client.get_single_template_with_metadata(template_id, region)
            self._check_resp(smresp, smbody, apiname)

        if updateStackName == 0:
            print "Create a stack named UPDATE_123 so that I can verify " \
                  "more api calls"

        if self.fail_flag == 0:
            print "All api's are up!"
        elif self.fail_flag > 0:
            print "One or more api's failed. Look above."
            self.fail("One or more api's failed.")

        # #suspend stack, wait 1 min
        # print "suspend stack"
        # ssresp, ssbody = self.orchestration_client.suspend_stack(stack_name,
        # region)
        # self._check_resp(ssresp, ssbody, "suspend stack")
        #
        # time.sleep(60)
        #
        # #resume stack
        # print "resume stack"
        # rsresp, rsbody = self.client.resume_stack(stack_id, region)
        # self._check_resp(rsresp, rsbody, "resume stack")

    def _send_deploy_time_graphite(self, env, region, template, deploy_time,
                                   buildfail):
        cmd = 'echo "heat.' + env + '.build-tests.' + region + '.' + template \
              + '.' + buildfail + '  ' + str(deploy_time) \
              + ' `date +%s`" | ' \
                'nc graphite.staging.rs-heat.com ' \
                '2003 -q 2'
        #print cmd
        os.system(cmd)
        print "Deploy time sent to graphite"

    def _check_resp(self, resp, body, apiname):
        match = re.search('5[0-9][0-9]', resp['status']) or \
            re.search('404', resp['status'])
        if match:
            print "%s did not work. The response is: %s %s" % (apiname,
                                                    resp['status'], body)
            self.fail_flag += 1
        else:
            print "%s worked! The response is: %s" % (apiname, resp['status'])
        # if resp['status'] == '200' or resp['status'] == '201' or \
        #                 resp['status']== '202' or resp['status'] == '204':
        #     print "%s worked! The response is: %s" % (apiname, resp['status'])
        # else:
        #     print "%s did not work. The response is: %s %s" % (apiname,
        #                                                        resp['status'],
        #                                                        body)

    def _get_stacks(self, typestack, body, region):

        for stackname in body:
            match = re.search(typestack + '_*', stackname['stack_name'])
            if match and (stackname['stack_status'] not in
                ['CREATE_IN_PROGRESS', 'ADOPT_FAILED',
                               'ADOPT_IN_PROGRESS', 'DELETE_FAILED']):
                #print stackname
                ssresp, ssbody = self.orchestration_client.show_stack(
                    stackname['stack_name'], stackname['id'], region)
                #print ssresp
                #print ssbody
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