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


LOG = logging.getLogger(__name__)

adopt_data2 = """
{"status": "COMPLETE", "name": "ADOPT_554748", "stack_user_project_id": "883286", "environment": {"parameters": {"server_hostname": "WordPress", "username": "wp_user", "domain": "example1234.com", "image": "Ubuntu 12.04 LTS (Precise Pangolin) (PVHVM)", "chef_version": "11.16.2", "prefix": "wp_", "version": "3.9.2", "flavor": "2 GB Performance", "database_name": "wordpress", "kitchen": "https://github.com/rackspace-orchestration-templates/wordpress-single.git"}, "resource_registry": {"resources": {}}}, "template": {"parameter_groups": [{"parameters": ["server_hostname", "image", "flavor"], "label": "Server Settings"}, {"parameters": ["domain", "username"], "label": "WordPress Settings"}, {"parameters": ["kitchen", "chef_version", "version", "prefix"], "label": "rax-dev-params"}], "heat_template_version": "2013-05-23", "description": "This is a Heat template to deploy a single Linux server running WordPress.\\n", "parameters": {"server_hostname": {"default": "WordPress", "label": "Server Name", "type": "string", "description": "Hostname to use for the server that\'s built.", "constraints": [{"length": {"max": 64, "min": 1}}, {"allowed_pattern": "^[a-zA-Z][a-zA-Z0-9-]*$", "description": "Must begin with a letter and contain only alphanumeric characters.\\n"}]}, "username": {"default": "wp_user", "label": "Username", "type": "string", "description": "Username for system, database, and WordPress logins.", "constraints": [{"allowed_pattern": "^[a-zA-Z0-9 _.@-]{1,16}$", "description": "Must be shorter than 16 characters and may only contain alphanumeric\\ncharacters, \' \', \'_\', \'.\', \'@\', and/or \'-\'.\\n"}]}, "domain": {"default": "example.com", "label": "Site Domain", "type": "string", "description": "Domain to be used with WordPress site", "constraints": [{"allowed_pattern": "^[a-zA-Z0-9.-]{1,255}.[a-zA-Z]{2,15}$", "description": "Must be a valid domain name"}]}, "database_name": {"default": "wordpress", "label": "Database Name", "type": "string", "description": "WordPress database name", "constraints": [{"allowed_pattern": "^[0-9a-zA-Z$_]{1,64}$", "description": "Maximum length of 64 characters, may only contain letters, numbers, and\\nunderscores.\\n"}]}, "chef_version": {"default": "11.16.2", "type": "string", "description": "Version of chef client to use", "label": "Chef Version"}, "prefix": {"default": "wp_", "label": "Database Prefix", "type": "string", "description": "Prefix to use for WordPress database tables", "constraints": [{"allowed_pattern": "^[0-9a-zA-Z$_]{0,10}$", "description": "Prefix must be shorter than 10 characters, and can only include\\nletters, numbers, $, and/or underscores.\\n"}]}, "version": {"default": "3.9.2", "label": "WordPress Version", "type": "string", "description": "Version of WordPress to install", "constraints": [{"allowed_values": ["3.9.2"]}]}, "flavor": {"default": "1 GB Performance", "label": "Server Size", "type": "string", "description": "Required: Rackspace Cloud Server flavor to use. The size is based on the\\namount of RAM for the provisioned server.\\n", "constraints": [{"description": "Must be a valid Rackspace Cloud Server flavor for the region you have\\nselected to deploy into.\\n", "allowed_values": ["1 GB Performance", "2 GB Performance", "4 GB Performance", "8 GB Performance", "15 GB Performance", "30 GB Performance", "1GB Standard Instance", "2GB Standard Instance", "4GB Standard Instance", "8GB Standard Instance", "15GB Standard Instance", "30GB Standard Instance"]}]}, "image": {"default": "Ubuntu 12.04 LTS (Precise Pangolin) (PVHVM)", "label": "Operating System", "type": "string", "description": "Required: Server image used for all servers that are created as a part of\\nthis deployment.\\n", "constraints": [{"description": "Must be a supported operating system.", "allowed_values": ["Ubuntu 12.04 LTS (Precise Pangolin)"]}]}, "kitchen": {"default": "https://github.com/rackspace-orchestration-templates/wordpress-single.git", "type": "string", "description": "URL for a git repo containing required cookbooks", "label": "Kitchen URL"}}, "outputs": {"mysql_root_password": {"description": "MySQL Root Password", "value": {"get_attr": ["mysql_root_password", "value"]}}, "wordpress_password": {"description": "WordPress Password", "value": {"get_attr": ["database_password", "value"]}}, "private_key": {"description": "SSH Private Key", "value": {"get_attr": ["ssh_key", "private_key"]}}, "server_ip": {"description": "Server IP", "value": {"get_attr": ["wordpress_server", "accessIPv4"]}}, "wordpress_user": {"description": "WordPress User", "value": {"get_param": "username"}}}, "resources": {"sync_key": {"type": "OS::Nova::KeyPair", "properties": {"name": {"str_replace": {"params": {"%stack_id%": {"get_param": "OS::stack_id"}}, "template": "%stack_id%-sync"}}, "save_private_key": true}}, "wp_secure_auth": {"type": "OS::Heat::RandomString", "properties": {"length": 32, "sequence": "hexdigits"}}, "wordpress_server": {"type": "Rackspace::Cloud::Server", "properties": {"key_name": {"get_resource": "ssh_key"}, "flavor": {"get_param": "flavor"}, "image": {"get_param": "image"}, "name": {"get_param": "server_hostname"}, "metadata": {"rax-heat": {"get_param": "OS::stack_id"}}}}, "mysql_root_password": {"type": "OS::Heat::RandomString", "properties": {"length": 16, "sequence": "lettersdigits"}}, "mysql_debian_password": {"type": "OS::Heat::RandomString", "properties": {"length": 16, "sequence": "lettersdigits"}}, "ssh_key": {"type": "OS::Nova::KeyPair", "properties": {"name": {"get_param": "OS::stack_id"}, "save_private_key": true}}, "wp_auth": {"type": "OS::Heat::RandomString", "properties": {"length": 32, "sequence": "hexdigits"}}, "wordpress_setup": {"depends_on": "wordpress_server", "type": "OS::Heat::ChefSolo", "properties": {"node": {"varnish": {"version": "3.0", "listen_port": "80"}, "sysctl": {"values": {"fs.inotify.max_user_watches": 1000000}}, "lsyncd": {"interval": 5}, "monit": {"mail_format": {"from": "monit@localhost"}, "notify_email": "root@localhost"}, "vsftpd": {"chroot_local_user": false, "ssl_ciphers": "AES256-SHA", "write_enable": true, "local_umask": "002", "hide_ids": false, "ssl_enable": true, "ipaddress": ""}, "wordpress": {"keys": {"logged_in": {"get_attr": ["wp_logged_in", "value"]}, "secure_auth_key": {"get_attr": ["wp_secure_auth", "value"]}, "nonce_key": {"get_attr": ["wp_nonce", "value"]}, "auth": {"get_attr": ["wp_auth", "value"]}}, "server_aliases": [{"get_param": "domain"}], "version": {"get_param": "version"}, "db": {"host": "127.0.0.1", "user": {"get_param": "username"}, "name": {"get_param": "database_name"}, "pass": {"get_attr": ["database_password", "value"]}}, "dir": {"str_replace": {"params": {"%domain%": {"get_param": "domain"}}, "template": "/var/www/vhosts/%domain%"}}}, "run_list": ["recipe[apt]", "recipe[build-essential]", "recipe[rax-wordpress::apache-prep]", "recipe[sysctl::attribute_driver]", "recipe[mysql::server]", "recipe[rax-wordpress::mysql]", "recipe[hollandbackup]", "recipe[hollandbackup::mysqldump]", "recipe[hollandbackup::main]", "recipe[hollandbackup::backupsets]", "recipe[hollandbackup::cron]", "recipe[rax-wordpress::x509]", "recipe[memcached]", "recipe[php]", "recipe[rax-install-packages]", "recipe[wordpress]", "recipe[rax-wordpress::wp-setup]", "recipe[rax-wordpress::user]", "recipe[rax-wordpress::memcache]", "recipe[lsyncd]", "recipe[vsftpd]", "recipe[rax-wordpress::vsftpd]", "recipe[varnish::repo]", "recipe[varnish]", "recipe[rax-wordpress::apache]", "recipe[rax-wordpress::varnish]", "recipe[rax-wordpress::firewall]", "recipe[rax-wordpress::vsftpd-firewall]", "recipe[rax-wordpress::lsyncd]"], "mysql": {"remove_test_database": true, "server_debian_password": {"get_attr": ["mysql_debian_password", "value"]}, "server_root_password": {"get_attr": ["mysql_root_password", "value"]}, "bind_address": "127.0.0.1", "remove_anonymous_users": true, "server_repl_password": {"get_attr": ["mysql_repl_password", "value"]}}, "apache": {"listen_ports": [8080], "serversignature": "Off", "traceenable": "Off", "timeout": 30}, "memcached": {"listen": "127.0.0.1"}, "hollandbackup": {"main": {"mysqldump": {"host": "localhost", "password": {"get_attr": ["mysql_root_password", "value"]}, "user": "root"}, "backup_directory": "/var/lib/mysqlbackup"}}, "rax": {"apache": {"domain": {"get_param": "domain"}}, "varnish": {"master_backend": "localhost"}, "packages": ["php5-imagick"], "wordpress": {"admin_pass": {"get_attr": ["database_password", "value"]}, "admin_user": {"get_param": "username"}, "user": {"group": {"get_param": "username"}, "name": {"get_param": "username"}}}, "lsyncd": {"ssh": {"private_key": {"get_attr": ["sync_key", "private_key"]}}}}}, "username": "root", "private_key": {"get_attr": ["ssh_key", "private_key"]}, "host": {"get_attr": ["wordpress_server", "accessIPv4"]}, "chef_version": {"get_param": "chef_version"}, "kitchen": {"get_param": "kitchen"}}}, "database_password": {"type": "OS::Heat::RandomString", "properties": {"length": 16, "sequence": "lettersdigits"}}, "wp_logged_in": {"type": "OS::Heat::RandomString", "properties": {"length": 32, "sequence": "hexdigits"}}, "mysql_repl_password": {"type": "OS::Heat::RandomString", "properties": {"length": 16, "sequence": "lettersdigits"}}, "wp_nonce": {"type": "OS::Heat::RandomString", "properties": {"length": 32, "sequence": "hexdigits"}}}}, "action": "UPDATE", "project_id": "883286", "id": "b10bfa80-e495-40d7-bb5a-f663f514c804", "resources": {"sync_key": {"status": "COMPLETE", "name": "sync_key", "resource_data": {"private_key": "-----BEGIN RSA PRIVATE KEY-----\\nMIIEpAIBAAKCAQEAxPfyF/OT4yzSOBmH8yYtC3OB37Kd17jPvpdE0kAuRoWYAcyV\\nCTOn9z9XgmB4wjllC1Jbs/YqHh5m3ygQUMxHES8cf6AoCmH/oM1JdHUFgvRe8W8s\\nDNqUdhuuHRiiV9jD2sv30hnCNtyNJuBPgSYjV0xM0LmY1k2WVFmpLaFf+sd0cIGD\\nfUYcELSdnmgCz2LAESZgkmay1sY0FCpLcorVhTGcw7GNvRpQSApdWpq6D//+0lIL\\npneyUzziX6uYYOuCTxSJVKJk14IyTSakbfgFlrNFLIh5CZme+uCM9o6rDbJgCcMa\\nQdPstwfJbUcCpWC9t4Hl5rA/37/0tWMXITCg7QIDAQABAoIBAQCDU43mylDgNxIy\\ntVMfm2SNLgZ5z+3N1zssKE+Kn6A7BPfEu1LjP73N7D28f/YECaCFW/QomQib7ElK\\noLvAI3N+0Zp+vZn00kJORJGlRCDYn3ZuI2GLcHFsDiiY3cPgLnbnevdQ7ju/uG2k\\nbgqUYYlOu2C8CgMNX83Lj7xs4BvOZ+EDfOY9dAU37D9oahjTNLSR4XpkpsAgrXi0\\nTW+Hqx3MFK9DtVxYqr8+4REzZlxkpSQU5ipTOP6TwxMtKooN8qB5fGaAY3lQIWgH\\n29Oy3tBn2WO948qoZbJqDogVIn9i743ldnEYU5hJ8bWr0NhGdGY6yZDtRjiUipbA\\nXzeMwmFBAoGBAPjn2vMRKcFwoztOAqtvdu+KUD2w2tjR7JgzlcbHf3qFBMwMY6FQ\\nQCyK8S2X/LfMi/H+prxrsaISvm70bTvHBbSjYrts17CQzERcmdlBTvIecskTP6M7\\n4Ht7VU7sjOWfhgFT/5o/qaxgL+D/F4veO21u8Nq6aLfW3a3tLnAz4FJbAoGBAMqV\\nIU3+qGI96kCKdUUEil/oegNZVmSFYTGRPcmhO7FKrsOjH53KRJSLIkdbLeYT0zzD\\nHHTbhA+dYRHt7bRKbUPN1WzPpH7q+LecWaNv2zT9NaMNJeoSznKdcOOnVPwMUQRR\\nECPG5RGT/v/JKtjJIj1aYMscBVFSczlQL3M09yxXAoGAB1pSDXwkT6KUL9xOF+Jj\\nERB07l2bGWyaIKTld8nM6kGjsqNrDgjg3G/+T+p9fLB+Mdfj9Qz5YmBLX9u4nlty\\nv7NT51V/yad9YUebA9/6BQ0BNw9qgdfy+bLbAknan63mt4NTuarHyF/PCkZ+25Ll\\nDoaIdu2qykN+qPSouofNyKECgYBpaDcwEfUjSPv+IQzroHUvehMicvWU0CHGXMA9\\njXs1wJo2iUYGIByW/d4UKskzEdWzpAHGfAG27jh3z8kDKka4JP2L5G6+6xwGzX+G\\nnsj8RVQHRuwXYzmwQWNf0M1TaEUvbc5sDy1ZfBwOk2mL6vu52LDMfgP2UGRLygEm\\nfMSveQKBgQCEXBICU51DmMtkkshrbZuvYyNQ+vZ7D6mGLZcF7rzcYBwhieDs6jDq\\n5yfD/WmtNHPER7vgSekXsB0Z9QPN3FAKhhXUNeIFH0780P+vnR8iuCc1p4QmySGW\\nJi/fF1kCdJKTYlFtGSd/Q6PELn6brD41lVnm/MCfYGw7Q06zdxDnHg==\\n-----END RSA PRIVATE KEY-----\\n"}, "resource_id": "b10bfa80-e495-40d7-bb5a-f663f514c804-sync", "action": "CREATE", "type": "OS::Nova::KeyPair", "metadata": {}}, "wp_secure_auth": {"status": "COMPLETE", "name": "wp_secure_auth", "resource_data": {"value": "30BA76B73A52FAC6DBEBE265AD6C2617"}, "resource_id": "30BA76B73A52FAC6DBEBE265AD6C2617", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}, "wordpress_server": {"status": "COMPLETE", "name": "wordpress_server", "resource_data": {"private_key": "-----BEGIN RSA PRIVATE KEY-----\\nMIICXAIBAAKBgQDlcT+x9kDr/J9cd3G9ep9T6UPCGGCunB+h1xO2SuJdwe5AJkPc\\nDPWT/BGncIyq5PdHwIB9w/PNRbe015GvdMh9ToIK539G2gv/F8denVLv5VRRPL2k\\nmO5uCn273LqK4kiuTP65WQWj+HDpQBAiB6r2VQh0S4DR1JadmbR2c5clhwIDAQAB\\nAoGAAdzNe5BYLpI6aPG/Rp58NJ4sIqM4BbLWvuWUD2LEO6abXIHzAxJH3A+rxQQw\\n4CJDr51sbZjtnbj3KMynLhlwly/ghZrP+a7fwwD6S30W/8qItzfO3YFLbTxEUhK4\\nOU3oMNMgRGq6shuKkYJVwt4fKESpDmryxcZr3TOFyvsffyECQQDuVOB1yuQE1ulE\\nL+9lUz3evtSNOyrDD8pu75UftJ9rcObTuk470Vc/gl5YmaymOuV6GDExjG1DR4k5\\nr0BJG/+7AkEA9nOruhZQI23tDLYBzO/fe8DqJdh16KtgYvyqFmJMmrHkrLYzxwPG\\n1XqMZO031807SfC0qb4mZiydVPSbvX/WpQJAFM4R/hZlC0sbd9lbY5P9rako8t88\\nX2TMfhyp/ueMlxt2+vqjg7NFk4S06bUYjjZL+/mKqdGhZCMlhoSW7wrjqwJBAOZi\\nGxZJ5YA5Mm+/dM9vLSsym6/lOdPW4LOoHhfurE2wHmSVrrFMBoNpm/R9DMbfQ51L\\nNpe2+Y5qBml0gGIVL0ECQBHoLdqvn/zuL9zWDshdjcdu2dKaQtImMyC7DGx/ouNG\\nw6kTXE6vwCIBhcXbipSa3MyH+If78m4tqGcnCh6PqGI=\\n-----END RSA PRIVATE KEY-----"}, "resource_id": "e45541dc-7d6c-4ada-bdd6-b6e8c27c7d2b", "action": "CREATE", "type": "Rackspace::Cloud::Server", "metadata": {}}, "mysql_root_password": {"status": "COMPLETE", "name": "mysql_root_password", "resource_data": {"value": "xmBpiAQU5a3q9lsF"}, "resource_id": "xmBpiAQU5a3q9lsF", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}, "mysql_debian_password": {"status": "COMPLETE", "name": "mysql_debian_password", "resource_data": {"value": "kOIKVAaIpItvS8yM"}, "resource_id": "kOIKVAaIpItvS8yM", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}, "ssh_key": {"status": "COMPLETE", "name": "ssh_key", "resource_data": {"private_key": "-----BEGIN RSA PRIVATE KEY-----\\nMIIEpAIBAAKCAQEAwwWQFqJWvP+0mRhnJSHQIDNEj9BFskQLe2n++0SZgGP7fb22\\nw3DtjZ9iSKQ2tFJmCb3OscZQDZx+IG/PtFD/GbDgSZHA6hBzgYMFEkW1fSHj/g2Y\\n2W3FQplxBIA9uBV62M+ILpn1xw/SLQgFvbBzetOpr6/mMiswLUqxVdc53KxnAF/F\\nXbfThSFfGtLb6z7DA7MP1J7SVqz6xggtCUGYzudLYm4DTIj3TPkloyXuFdLpb4+R\\nqhmRpSq9Jt02ZUsPMdg9Jqhk9CeFhkZFsy7SBS+NsfiB++wVAIQF7VtE0gFk3WwC\\nsU6gwpMSYTFxf9i4ovyrBgLZ2Vc73IBFrRx8zwIDAQABAoIBAB4skiquW3VKqwq0\\n9+CK5sTUqdsGgoIefRhPQiBmcMmorpS58bkzk83Bx1ct8TjdNuRy9bQT1vcEK4+h\\nPSXNEmtLLqizYIHWoch8GSDGoFoIEFqSh/+8ODUhwJbNsL72s9cv5QYw1BJEpGRL\\nRXggAP4UGcERGjDQ9ddMIzwA3PcDgJaTJ/O9umzdTGiQsXDOYW7YGJNS6akZPkhr\\nbccLIzUA/PkAZdf+j6Q9zzWE1cBHYwZ6e/HcqIy7ElIvctvnVPL1Oizsnt7/lVz7\\n7KgQcT0VB4UiADJJrBbQjChUpuldeoZi3IYUDRmPrYBWLSELVFok/jD2AKViqaoV\\n464xYgECgYEA4e3bHLMgfQnCqvt4Pzy7hcof31Rbra4/2//zRCNDg8V5JWxNh3dh\\nWx9A5W24evuMU7Zu62eiYXuASUZt6ZxsIgETkCm540MKBMSfqDcFRSydRDmUEw25\\nN8An7639HluOkF8PlYl8PtfQLdMAHsaa9/s6+uqyRJdZGIRDKzi9UQ8CgYEA3PqX\\nRwpid6QTCGYeEhc9ZrMF0szseOFPJJbG5Jg1xQ1dIfkFWPuE7jWpN74pZ0JWqMMw\\nI+CyGmpoVKPmPD1AqN2z4idGeIMA6iv08GUcFgw4F1OYToGxPS0OJsl/F0OKqmLB\\nvjlHJK2++l47fFl+psP/r1m4J4BRk59YH4B2mEECgYEAmW5qHmx7xM7LGEkdGX0K\\nMMraqFVmyWWL0sFYmM6F/EgwhLyvTi9Bu5tW/DhuT37jhrpfS5keyqsPrTOaU0s6\\nmEE44u+jYPZXKHPLpXZwKtEooHul1ua8AWOK+5eiTWqKP/t+3uP2r8rqgyRHcZ8Z\\nAQ3puRuII1LRW/f+kay/zPsCgYAQZM7gSFbxxUxcLSdB9FNr0RA3iVhpx11Vu5HZ\\n16j1i35DTPQmm9JK0dRR/FuZ+4PuVTy3DK5p40cGMHqeMXUgkgIMXxmNSzrAJK6x\\nPu8Me6+Vm3ALMvfxL+yC2CQDl9ErvtPcxucOQ42NiXwkR4dr29KWMbPFynFC4Glr\\nPN6PgQKBgQDK89IhMt3IeSUcBl4oEKpCrKPOapbIlEETCVCNAMesB1lnr7qGGJNZ\\nWXHiNzJ207NeXfNxvnnn4MgR7EnZR0U3rxco5danwBQ05VUfApL3mqXcTJMl2ntV\\nJpNLjtqJJgu7trxFpo2PCXFPQHKDitDiBi9WSE4jqqTu7uJNSq7KrA==\\n-----END RSA PRIVATE KEY-----\\n"}, "resource_id": "b10bfa80-e495-40d7-bb5a-f663f514c804", "action": "CREATE", "type": "OS::Nova::KeyPair", "metadata": {}}, "wp_auth": {"status": "COMPLETE", "name": "wp_auth", "resource_data": {"value": "2F8369B266B2C92CF7A1A5DB841443F3"}, "resource_id": "2F8369B266B2C92CF7A1A5DB841443F3", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}, "wordpress_setup": {"status": "COMPLETE", "name": "wordpress_setup", "resource_data": {"process_id": "24089"}, "resource_id": "8cc78f9d-4066-4f6c-9876-ace25ca83f30", "action": "CREATE", "type": "OS::Heat::ChefSolo", "metadata": {}}, "database_password": {"status": "COMPLETE", "name": "database_password", "resource_data": {"value": "TPAGoiCwash9T1fi"}, "resource_id": "TPAGoiCwash9T1fi", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}, "wp_logged_in": {"status": "COMPLETE", "name": "wp_logged_in", "resource_data": {"value": "026611BAE58FDE37C69E2F2EDB563EB2"}, "resource_id": "026611BAE58FDE37C69E2F2EDB563EB2", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}, "mysql_repl_password": {"status": "COMPLETE", "name": "mysql_repl_password", "resource_data": {"value": "3kRxPiIAt8xksyXA"}, "resource_id": "3kRxPiIAt8xksyXA", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}, "wp_nonce": {"status": "COMPLETE", "name": "wp_nonce", "resource_data": {"value": "705CC92E02C3F6877C27EFD5B4925D0F"}, "resource_id": "705CC92E02C3F6877C27EFD5B4925D0F", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}}}
"""

adopt_data3 = """
{"status": "COMPLETE", "name": "ADOPT_98324", "stack_user_project_id": "897502", "environment": {"parameter_defaults": {}, "parameters": {"username": "wp_user", "domain": "example.com", "chef_version": "11.16.2", "wp_web_server_flavor": "2 GB General Purpose v1", "wp_web_server_hostnames": "WordPress-Web%index%", "image": "Ubuntu 12.04 LTS (Precise Pangolin) (PVHVM)", "load_balancer_hostname": "WordPress-Load-Balancer", "child_template": "https://raw.githubusercontent.com/rackspace-orchestration-templates/wordpress-multi/master/wordpress-web-server.yaml", "wp_master_server_hostname": "WordPress-Master", "prefix": "wp_", "version": "3.9.2", "wp_master_server_flavor": "2 GB General Purpose v1", "database_name": "wordpress", "wp_web_server_count": "1", "database_server_flavor": "4 GB General Purpose v1", "database_server_hostname": "WordPress-Database", "kitchen": "https://github.com/rackspace-orchestration-templates/wordpress-multi"}, "resource_registry": {"resources": {}, "https://raw.githubusercontent.com/rackspace-orchestration-templates/wordpress-multi/master/wordpress-web-server.yaml": "https://raw.githubusercontent.com/rackspace-orchestration-templates/wordpress-multi/master/wordpress-web-server.yaml"}}, "template": {"parameter_groups": [{"parameters": ["image"], "label": "Server Settings"}, {"parameters": ["wp_master_server_flavor", "wp_web_server_count", "wp_web_server_flavor"], "label": "Web Server Settings"}, {"parameters": ["database_server_flavor"], "label": "Database Settings"}, {"parameters": ["domain", "username"], "label": "WordPress Settings"}, {"parameters": ["kitchen", "chef_version", "child_template", "version", "prefix", "load_balancer_hostname", "wp_web_server_hostnames", "wp_master_server_hostname", "database_server_hostname"], "label": "rax-dev-params"}], "heat_template_version": "2013-05-23", "description": "This is a Heat template to deploy Load Balanced WordPress servers with a\\nbackend database server.\\n", "parameters": {"username": {"default": "wp_user", "label": "Username", "type": "string", "description": "Username for system, database, and WordPress logins.", "constraints": [{"allowed_pattern": "^[a-zA-Z0-9 _.@-]{1,16}$", "description": "Must be shorter than 16 characters and may only contain alphanumeric\\ncharacters, \' \', \'_\', \'.\', \'@\', and/or \'-\'.\\n"}]}, "domain": {"default": "example.com", "label": "Site Domain", "type": "string", "description": "Domain to be used with this WordPress site", "constraints": [{"allowed_pattern": "^[a-zA-Z0-9.-]{1,255}.[a-zA-Z]{2,15}$", "description": "Must be a valid domain name"}]}, "chef_version": {"default": "11.16.2", "type": "string", "description": "Version of chef client to use", "label": "Chef Version"}, "wp_web_server_flavor": {"default": "2 GB General Purpose v1", "label": "Node Server Size", "type": "string", "description": "Cloud Server size to use on all of the additional web nodes.\\n", "constraints": [{"description": "Must be a valid Rackspace Cloud Server flavor for the region you have\\nselected to deploy into.\\n", "allowed_values": ["1 GB General Purpose v1", "2 GB General Purpose v1", "4 GB General Purpose v1", "8 GB General Purpose v1", "15 GB I/O v1", "30 GB I/O v1", "1GB Standard Instance", "2GB Standard Instance", "4GB Standard Instance", "8GB Standard Instance", "15GB Standard Instance", "30GB Standard Instance"]}]}, "wp_web_server_hostnames": {"default": "WordPress-Web%index%", "label": "Server Name", "type": "string", "description": "Hostname to use for all additional WordPress web nodes", "constraints": [{"length": {"max": 64, "min": 1}}, {"allowed_pattern": "^[a-zA-Z][a-zA-Z0-9%-]*$", "description": "Must begin with a letter and contain only alphanumeric characters.\\n"}]}, "image": {"default": "Ubuntu 12.04 LTS (Precise Pangolin) (PVHVM)", "label": "Operating System", "type": "string", "description": "Required: Server image used for all servers that are created as a part of\\nthis deployment.\\n", "constraints": [{"description": "Must be a supported operating system.", "allowed_values": ["Ubuntu 12.04 LTS (Precise Pangolin) (PVHVM)"]}]}, "load_balancer_hostname": {"default": "WordPress-Load-Balancer", "label": "Load Balancer Hostname", "type": "string", "description": "Hostname for the Cloud Load Balancer", "constraints": [{"length": {"max": 64, "min": 1}}, {"allowed_pattern": "^[a-zA-Z][a-zA-Z0-9-]*$", "description": "Must begin with a letter and contain only alphanumeric characters.\\n"}]}, "child_template": {"default": "https://raw.githubusercontent.com/rackspace-orchestration-templates/wordpress-multi/master/wordpress-web-server.yaml", "type": "string", "description": "Location of the child template to use for the WordPress web servers\\n", "label": "Child Template"}, "wp_master_server_hostname": {"default": "WordPress-Master", "label": "Server Name", "type": "string", "description": "Hostname to use for your WordPress web-master server.", "constraints": [{"length": {"max": 64, "min": 1}}, {"allowed_pattern": "^[a-zA-Z][a-zA-Z0-9-]*$", "description": "Must begin with a letter and contain only alphanumeric characters.\\n"}]}, "prefix": {"default": "wp_", "label": "Wordpress Prefix", "type": "string", "description": "Prefix to use for database table names.", "constraints": [{"allowed_pattern": "^[0-9a-zA-Z$_]{0,10}$", "description": "Prefix must be shorter than 10 characters, and can only include\\nletters, numbers, $, and/or underscores.\\n"}]}, "version": {"default": "3.9.2", "label": "WordPress Version", "type": "string", "description": "Version of WordPress to install", "constraints": [{"allowed_values": ["3.9.2"]}]}, "wp_master_server_flavor": {"default": "2 GB General Purpose v1", "label": "Master Server Size", "type": "string", "description": "Cloud Server size to use for the web-master node. The size should be at\\nleast one size larger than what you use for the web nodes. This server\\nhandles all admin calls and will ensure files are synced across all\\nother nodes.\\n", "constraints": [{"description": "Must be a valid Rackspace Cloud Server flavor for the region you have\\nselected to deploy into.\\n", "allowed_values": ["1 GB General Purpose v1", "2 GB General Purpose v1", "4 GB General Purpose v1", "8 GB General Purpose v1", "15 GB I/O v1", "30 GB I/O v1", "1GB Standard Instance", "2GB Standard Instance", "4GB Standard Instance", "8GB Standard Instance", "15GB Standard Instance", "30GB Standard Instance"]}]}, "database_name": {"default": "wordpress", "label": "Database Name", "type": "string", "description": "WordPress database name", "constraints": [{"allowed_pattern": "^[0-9a-zA-Z$_]{1,64}$", "description": "Maximum length of 64 characters, may only contain letters, numbers, and\\nunderscores.\\n"}]}, "wp_web_server_count": {"default": 1, "label": "Web Server Count", "type": "number", "description": "Number of web servers to deploy in addition to the web-master", "constraints": [{"range": {"max": 7, "min": 0}, "description": "Must be between 0 and 7 servers."}]}, "database_server_flavor": {"default": "4 GB General Purpose v1", "label": "Server Size", "type": "string", "description": "Cloud Server size to use for the database server. Sizes refer to the\\namount of RAM allocated to the server.\\n", "constraints": [{"description": "Must be a valid Rackspace Cloud Server flavor for the region you have\\nselected to deploy into.\\n", "allowed_values": ["2 GB General Purpose v1", "4 GB General Purpose v1", "8 GB General Purpose v1", "15 GB I/O v1", "30 GB I/O v1", "2GB Standard Instance", "4GB Standard Instance", "8GB Standard Instance", "15GB Standard Instance", "30GB Standard Instance"]}]}, "database_server_hostname": {"default": "WordPress-Database", "label": "Server Name", "type": "string", "description": "Hostname to use for your WordPress Database Server", "constraints": [{"length": {"max": 64, "min": 1}}, {"allowed_pattern": "^[a-zA-Z][a-zA-Z0-9-]*$", "description": "Must begin with a letter and contain only alphanumeric characters.\\n"}]}, "kitchen": {"default": "https://github.com/rackspace-orchestration-templates/wordpress-multi", "type": "string", "description": "URL for the kitchen to use, fetched using git\\n", "label": "Kitchen"}}, "outputs": {"private_key": {"description": "SSH Private IP", "value": {"get_attr": ["ssh_key", "private_key"]}}, "load_balancer_ip": {"description": "Load Balancer IP", "value": {"get_attr": ["load_balancer", "PublicIp"]}}, "mysql_root_password": {"description": "MySQL Root Password", "value": {"get_attr": ["mysql_root_password", "value"]}}, "wordpress_user": {"description": "WordPress User", "value": {"get_param": "username"}}, "wordpress_web_ips": {"description": "Web Server IPs", "value": {"get_attr": ["wp_web_servers", "accessIPv4"]}}, "wordpress_password": {"description": "WordPress Password", "value": {"get_attr": ["database_password", "value"]}}, "database_server_ip": {"description": "Database Server IP", "value": {"get_attr": ["database_server", "accessIPv4"]}}, "wordpress_web_master_ip": {"description": "Web-Master IP", "value": {"get_attr": ["wp_master_server", "accessIPv4"]}}}, "resources": {"load_balancer": {"depends_on": ["wp_master_server_setup", "wp_web_servers"], "type": "Rackspace::Cloud::LoadBalancer", "properties": {"protocol": "HTTP", "name": {"get_param": "load_balancer_hostname"}, "algorithm": "ROUND_ROBIN", "virtualIps": [{"ipVersion": "IPV4", "type": "PUBLIC"}], "contentCaching": "ENABLED", "healthMonitor": {"attemptsBeforeDeactivation": 2, "statusRegex": "^[23]0[0-2]$", "delay": 10, "timeout": 5, "path": "/", "type": "HTTP"}, "nodes": [{"addresses": [{"get_attr": ["wp_master_server", "privateIPv4"]}], "condition": "ENABLED", "port": 80}, {"addresses": {"get_attr": ["wp_web_servers", "privateIPv4"]}, "condition": "ENABLED", "port": 80}], "port": 80, "metadata": {"rax-heat": {"get_param": "OS::stack_id"}}}}, "sync_key": {"type": "OS::Nova::KeyPair", "properties": {"name": {"str_replace": {"params": {"%stack_id%": {"get_param": "OS::stack_id"}}, "template": "%stack_id%-sync"}}, "save_private_key": true}}, "database_server": {"type": "Rackspace::Cloud::Server", "properties": {"key_name": {"get_resource": "ssh_key"}, "flavor": {"get_param": "database_server_flavor"}, "image": {"get_param": "image"}, "name": {"get_param": "database_server_hostname"}, "metadata": {"rax-heat": {"get_param": "OS::stack_id"}}}}, "wp_web_servers": {"depends_on": "database_server", "type": "OS::Heat::ResourceGroup", "properties": {"count": {"get_param": "wp_web_server_count"}, "resource_def": {"type": {"get_param": "child_template"}, "properties": {"domain": {"get_param": "domain"}, "image": {"get_param": "image"}, "wp_nonce": {"get_attr": ["wp_nonce", "value"]}, "memcached_host": {"get_attr": ["database_server", "privateIPv4"]}, "prefix": {"get_param": "prefix"}, "ssh_private_key": {"get_attr": ["ssh_key", "private_key"]}, "lsync_pub": {"get_attr": ["sync_key", "public_key"]}, "wp_auth": {"get_attr": ["wp_auth", "value"]}, "version": {"get_param": "version"}, "chef_version": {"get_param": "chef_version"}, "username": {"get_param": "username"}, "wp_web_server_flavor": {"get_param": "wp_web_server_flavor"}, "varnish_master_backend": {"get_attr": ["wp_master_server", "privateIPv4"]}, "parent_stack_id": {"get_param": "OS::stack_id"}, "wp_logged_in": {"get_attr": ["wp_logged_in", "value"]}, "kitchen": {"get_param": "kitchen"}, "wp_secure_auth": {"get_attr": ["wp_secure_auth", "value"]}, "ssh_keypair_name": {"get_resource": "ssh_key"}, "database_name": {"get_param": "database_name"}, "wp_web_server_hostname": {"get_param": "wp_web_server_hostnames"}, "ssh_public_key": {"get_attr": ["ssh_key", "public_key"]}, "database_password": {"get_attr": ["database_password", "value"]}, "database_host": {"get_attr": ["database_server", "privateIPv4"]}}}}}, "wp_secure_auth": {"type": "OS::Heat::RandomString", "properties": {"length": 32, "sequence": "hexdigits"}}, "mysql_root_password": {"type": "OS::Heat::RandomString", "properties": {"length": 16, "sequence": "lettersdigits"}}, "mysql_debian_password": {"type": "OS::Heat::RandomString", "properties": {"length": 16, "sequence": "lettersdigits"}}, "wp_auth": {"type": "OS::Heat::RandomString", "properties": {"length": 32, "sequence": "hexdigits"}}, "ssh_key": {"type": "OS::Nova::KeyPair", "properties": {"name": {"get_param": "OS::stack_id"}, "save_private_key": true}}, "wp_master_server": {"type": "Rackspace::Cloud::Server", "properties": {"key_name": {"get_resource": "ssh_key"}, "flavor": {"get_param": "wp_master_server_flavor"}, "image": {"get_param": "image"}, "name": {"get_param": "wp_master_server_hostname"}, "metadata": {"rax-heat": {"get_param": "OS::stack_id"}}}}, "database_server_firewall": {"depends_on": "wp_master_server_setup", "type": "OS::Heat::ChefSolo", "properties": {"node": {"run_list": ["recipe[rax-wordpress::memcached-firewall]"], "rax": {"memcached": {"clients": [{"get_attr": ["wp_master_server", "privateIPv4"]}, {"get_attr": ["wp_web_servers", "privateIPv4"]}]}}}, "username": "root", "private_key": {"get_attr": ["ssh_key", "private_key"]}, "host": {"get_attr": ["database_server", "accessIPv4"]}, "chef_version": {"get_param": "chef_version"}, "kitchen": {"get_param": "kitchen"}}}, "database_server_setup": {"depends_on": "database_server", "type": "OS::Heat::ChefSolo", "properties": {"node": {"run_list": ["recipe[apt]", "recipe[build-essential]", "recipe[rax-firewall]", "recipe[mysql::server]", "recipe[rax-wordpress::memcached-firewall]", "recipe[memcached]", "recipe[rax-wordpress::mysql]", "recipe[rax-wordpress::mysql-firewall]", "recipe[hollandbackup]", "recipe[hollandbackup::mysqldump]", "recipe[hollandbackup::main]", "recipe[hollandbackup::backupsets]", "recipe[hollandbackup::cron]"], "memcached": {"memory": 500, "listen": {"get_attr": ["database_server", "privateIPv4"]}}, "hollandbackup": {"main": {"mysqldump": {"host": "localhost", "password": {"get_attr": ["mysql_root_password", "value"]}, "user": "root"}, "backup_directory": "/var/lib/mysqlbackup"}}, "rax": {"firewall": {"tcp": [22]}, "mysql": {"innodb_buffer_pool_mempercent": 0.6}}, "mysql": {"remove_test_database": true, "root_network_acl": ["10.%"], "server_debian_password": {"get_attr": ["mysql_debian_password", "value"]}, "server_root_password": {"get_attr": ["mysql_root_password", "value"]}, "bind_address": {"get_attr": ["database_server", "privateIPv4"]}, "remove_anonymous_users": true, "server_repl_password": {"get_attr": ["mysql_repl_password", "value"]}}}, "username": "root", "private_key": {"get_attr": ["ssh_key", "private_key"]}, "host": {"get_attr": ["database_server", "accessIPv4"]}, "chef_version": {"get_param": "chef_version"}, "kitchen": {"get_param": "kitchen"}}}, "wp_master_server_setup": {"depends_on": ["database_server_setup", "wp_web_servers"], "type": "OS::Heat::ChefSolo", "properties": {"node": {"varnish": {"version": "3.0", "listen_port": "80"}, "sysctl": {"values": {"fs.inotify.max_user_watches": 1000000}}, "lsyncd": {"interval": 5}, "monit": {"mail_format": {"from": "monit@localhost"}, "notify_email": "root@localhost"}, "vsftpd": {"chroot_local_user": false, "ssl_ciphers": "AES256-SHA", "write_enable": true, "local_umask": "002", "hide_ids": false, "ssl_enable": true, "ipaddress": ""}, "wordpress": {"keys": {"logged_in": {"get_attr": ["wp_logged_in", "value"]}, "secure_auth_key": {"get_attr": ["wp_secure_auth", "value"]}, "nonce_key": {"get_attr": ["wp_nonce", "value"]}, "auth": {"get_attr": ["wp_auth", "value"]}}, "server_aliases": [{"get_param": "domain"}], "version": {"get_param": "version"}, "db": {"host": {"get_attr": ["database_server", "privateIPv4"]}, "user": {"get_param": "username"}, "name": {"get_param": "database_name"}, "pass": {"get_attr": ["database_password", "value"]}}, "dir": {"str_replace": {"params": {"%domain%": {"get_param": "domain"}}, "template": "/var/www/vhosts/%domain%"}}}, "run_list": ["recipe[apt]", "recipe[build-essential]", "recipe[mysql::client]", "recipe[mysql-chef_gem]", "recipe[rax-wordpress::apache-prep]", "recipe[sysctl::attribute_driver]", "recipe[rax-wordpress::x509]", "recipe[php]", "recipe[rax-install-packages]", "recipe[rax-wordpress::wp-database]", "recipe[wordpress]", "recipe[rax-wordpress::wp-setup]", "recipe[rax-wordpress::user]", "recipe[rax-wordpress::memcache]", "recipe[lsyncd]", "recipe[vsftpd]", "recipe[rax-wordpress::vsftpd]", "recipe[varnish::repo]", "recipe[varnish]", "recipe[rax-wordpress::apache]", "recipe[rax-wordpress::varnish]", "recipe[rax-wordpress::varnish-firewall]", "recipe[rax-wordpress::firewall]", "recipe[rax-wordpress::vsftpd-firewall]", "recipe[rax-wordpress::lsyncd]"], "mysql": {"server_root_password": {"get_attr": ["mysql_root_password", "value"]}, "bind_address": {"get_attr": ["mysql_root_password", "value"]}}, "apache": {"listen_ports": [8080], "serversignature": "Off", "traceenable": "Off", "timeout": 30}, "rax": {"varnish": {"master_backend": "localhost"}, "lsyncd": {"clients": {"get_attr": ["wp_web_servers", "privateIPv4"]}, "ssh": {"private_key": {"get_attr": ["sync_key", "private_key"]}}}, "memcache": {"server": {"get_attr": ["database_server", "privateIPv4"]}}, "wordpress": {"admin_pass": {"get_attr": ["database_password", "value"]}, "admin_user": {"get_param": "username"}, "user": {"group": {"get_param": "username"}, "name": {"get_param": "username"}}}, "apache": {"domain": {"get_param": "domain"}}, "packages": ["php5-imagick"]}}, "username": "root", "private_key": {"get_attr": ["ssh_key", "private_key"]}, "host": {"get_attr": ["wp_master_server", "accessIPv4"]}, "chef_version": {"get_param": "chef_version"}, "kitchen": {"get_param": "kitchen"}}}, "wp_logged_in": {"type": "OS::Heat::RandomString", "properties": {"length": 32, "sequence": "hexdigits"}}, "mysql_repl_password": {"type": "OS::Heat::RandomString", "properties": {"length": 16, "sequence": "lettersdigits"}}, "database_password": {"type": "OS::Heat::RandomString", "properties": {"length": 16, "sequence": "lettersdigits"}}, "wp_nonce": {"type": "OS::Heat::RandomString", "properties": {"length": 32, "sequence": "hexdigits"}}}}, "action": "CREATE", "project_id": "897502", "id": "5cdde045-9767-46de-ab03-a8066725d5d4", "resources": {"load_balancer": {"status": "COMPLETE", "name": "load_balancer", "resource_data": {}, "resource_id": "75917", "action": "CREATE", "type": "Rackspace::Cloud::LoadBalancer", "metadata": {}}, "sync_key": {"status": "COMPLETE", "name": "sync_key", "resource_data": {"private_key": "-----BEGIN RSA PRIVATE KEY-----\\nMIIEpAIBAAKCAQEA01UNQNUXRMmXVIHQcIc+7Vop/Jzq2Tr4WD+YNjd24D2/2uzw\\nUy5/FWgqyhnxD2+QCUX2oAJBWBNENjaUxN6AuhWu7/iE4+qklVsOctaXh2kQwM8M\\n4dg6NSQXGosqgfb3uN5uLp7UBO7qj21STP0yn1l33O5Z8CNAfQl3GjYEWfZk4QAh\\nAbzalyjezmTUyHyyBt7rNBtkIP7Ck+kXI/AwPZc8P2t0aTFkAqzdH5yJl3ZiuOHV\\nRyxVXSLUxa7LvZ7dSCFdUUxfSwJnIIEz7Kw2wglSFLmWnc5/b1dW/htHPGFkdR7h\\nJTOkcKecJDRebfL8k5at5ezaww7GBDRZtG9LhwIDAQABAoIBAQDEs72KQs1NsXWx\\nqsKgesIPmoTKJCRT3ZeaTFcY37c+MTuKQk/OnNCc1EA/rLW7cFPYzc4oUPERUZ2D\\n+HmwZIncqqIRqnfGzHg0rHReX27bEugNDqsm62QCYn0+r5n5Li6VXDOiISOnE9ov\\ndcnM7z9XIqd2dEQySB2WRGEffHfAYu2Wjm8s7cGm5iOJPsFH2lWu8dU6wUZzoSRI\\nOZFSEHiI3KKWdUNGXZT6O2LmNZqLcNsnZcH16ZwT/Ki3IMKJRM+iQ0k7v2vPtz+t\\nenQ0cHEPIhMwrFoyZtJWMFBdOICwvLFWYWvkrxAfBZJ1o5YREBwgVaEb7Eg2IUer\\nBPMYjDyBAoGBAO4DfnCGnvQqKVOYMrCJ5MZq66kUkRK1hvZXQlbHEZU+mtwPUpYH\\nKe5JKrGEPQ7eUZt16itEA6xtYmL7J1idCdZmFpg79xNI/oDUXPacK1Lp/WY+PlUf\\nfjQQ0yV+prE1LYnApn0EL5871aZD5IlhV7+m+EVRof9u8EmrLGpo7jn/AoGBAONN\\nZB7S5DnwEjNaCwR9U+Bsepw3SIIl+NJ51PFDtxyeZ+5+fhYZo/d88JtEPzY6dJ9o\\nkPTMnrsCYdBaQJGJXl1wprSRsAx00x6Ur38XEqTtsEFOG1LSnPT/Fq6JdO44olY+\\nWJ7ssgNVkHOp5Z9yLLmU80bl9Gum8HcgNG2K9h55AoGAH/32O9fMe9NC9MqLXbFb\\nP9RVUsfB7DrcJjZ6Y0GkumPM2vFwT1wtJatOAshckKgPXg8OZ7xfpgiZ5eYOVtnc\\n3aWhOdstjbkNBHIHANri8+Uhu2F4bWarRwJP70VD0KPuOAreFgW/BO88+3k6ucCM\\n0+T0kBS16qiVwcExWig6hS8CgYBg1446m7tk++WlP03GYeckjNNITz1zRd5XPlT9\\nXc5cQRkiwX3SyKXVQcP5QwBziEA70n8/7RYLsx4dePZdi1tLED3WXOPWysdQFiUX\\nTqtA3YvkpvR5OwZoU25Eeof5HuP7PqDfRRUq2n+q583POwPXJaDoqfyTCRMWjgAI\\nU9Y8cQKBgQCz+r6kPrK/7m5h+amTCDPYexW103Dl5vOHyHI9NZjd8TmMVLB8Ciqp\\nwjHPiagtovuaewN/blJ5TBzTsTlbPCq2C6yyx91kCqSdbwdRwmYCmHn9zXynBtfq\\n/SwgrxYvi9kihyU+4tKMIOvJiOTj4sK+g75oLlcbTyXjtYiGkGBmkg==\\n-----END RSA PRIVATE KEY-----\\n"}, "resource_id": "5cdde045-9767-46de-ab03-a8066725d5d4-sync", "action": "CREATE", "type": "OS::Nova::KeyPair", "metadata": {}}, "database_server": {"status": "COMPLETE", "name": "database_server", "resource_data": {"private_key": "-----BEGIN RSA PRIVATE KEY-----\\nMIICXQIBAAKBgQDzp2UCIsm7nkO99JJBgLfPe+smZx76C9NPkDYzaLnds5Cwh6nx\\n9xi2Pu5EMq53+rycUO7BDgTRXoUrbLY28uM6h8gMdmjbGPlzKiM5h9s+4RWB51YS\\nLkCg9fWXeE+xszG7tbUzXM9zrU36x8IUD+c9kEYioNQ16qBEa4dawJP7GwIDAQAB\\nAoGBAOckujIYhoAyV9lwlv8E+VsgF6hK05wqc8Ba8tA6XXjwzCZrzND6tLrPYIHa\\nAqFXgG5aaOVEQ1XL8VGMxB/Es8INCAumhKaejVoKwURLM5rpkQsqSr+9DkuAIHT+\\nqEek5oNbf1HXS4ERjchcNLmT77LP1yJjctkFcmlEvfH5oy1BAkEA+K4xbJ+iMd/u\\n5/oQF7jrRLzqdgdqTEneZLwPt1ZwruJWO1jrWcs1encSIlSGDD16uKl0uBdMe52K\\nevIoXZg02QJBAPrTU47uiiNhsAlS+/YSdPViqyCkxXbhl92uQGyKexY0YkIJepkj\\nmebREgMCLTb/CKEeq9stfD/5MfrUpW8zJxMCQDRgI8K4AGY2vs+W6ErGxK5uh4ci\\nWq4EpNVckobPqt36h6TqPm9kEDhh2aznVnA/hphcAFxBc/dZH/BzDjNgOkkCQQCV\\nhMILsyC/hK0mccRm5Iu5925hkDdx7XrVF9mpmkdTbjigevwNK87DbB/bkUGYxiDD\\nwv/ZMN0fWZI0nuxbRFfnAkBe+T2qRAidQl4PJFxnWr/oS0Z/UPpSuDDy+lnMRha2\\nXXrIirE/bM5IsYfYfEsfTLvpwMpl9my8VZ/JEkIuu/O1\\n-----END RSA PRIVATE KEY-----"}, "resource_id": "dfe4a396-bb40-4779-9562-c6ecbc6f9e2c", "action": "CREATE", "type": "Rackspace::Cloud::Server", "metadata": {}}, "wp_web_servers": {"status": "COMPLETE", "name": "ADOPT_98324-wp_web_servers-nmyzh5ebxqjk", "stack_user_project_id": "897502", "environment": {"parameter_defaults": {}, "parameters": {}, "resource_registry": {"resources": {}, "https://raw.githubusercontent.com/rackspace-orchestration-templates/wordpress-multi/master/wordpress-web-server.yaml": "https://raw.githubusercontent.com/rackspace-orchestration-templates/wordpress-multi/master/wordpress-web-server.yaml"}}, "template": {"heat_template_version": "2013-05-23", "resources": {"0": {"type": "https://raw.githubusercontent.com/rackspace-orchestration-templates/wordpress-multi/master/wordpress-web-server.yaml", "properties": {"domain": "example.com", "image": "Ubuntu 12.04 LTS (Precise Pangolin) (PVHVM)", "wp_nonce": "E6E16A60BCE928B173C2E68BCAD8DA46", "memcached_host": "10.176.197.160", "prefix": "wp_", "ssh_private_key": "-----BEGIN RSA PRIVATE KEY-----\\nMIIEowIBAAKCAQEA1Kx41PKBXtyr15H9L0c5wYc9e9ZOcoQU101CHkeAH/Aj+Ucr\\nNZbRWubL8yhLosbNqlJq4PfWZoO4Rg6xBPcHmuu8Ty7TgYLHjxbdfbBcN/Ji9kAg\\nxRhgLYIoj46yY/9NYuQVuBYXe2hYnKZlWag2/XWomuDPtjM/L2ZvVmd8kIsxUinl\\nw+O37EXtWXc3YVoyakxtULSRjQ0fcNW3haSXmmUd+lWj6tVXporcx003rmd7ZyVg\\nCDyYhy7cxlZBQNo4JWIZvnKn5RxHUCAVTtOdTNF+eFfUxdMPvnBlJUbjZwyjVAFF\\nVXrZKUqnBfnrRo6/aua+zvwhUszmHlBRI2EBGQIDAQABAoIBADY2aO7Pio7l7aAc\\nBNBCdcSRdujUblbeuHlRpmMVkuGRU3o93BPjCCcF4kNvqCgsSUz7iWcjhjHHrfed\\n0x4S4otpQC1nIF9JORmOmJNrm3ZfgT6IhlH3rryrCy/dDjhTYiStQ6QTbZT1unDk\\nMb2zFaFylrI0UH5/fcHVeNgrtSMbAPvsSmldvh65d45jtxRf1/wo0WBnNHF7rypc\\nw6d6uFFxd5wiGSkMjir4A7k2Coiyq+LCjZHtRBXrNqFzPsWw4g7KBrQ9Af463JpR\\nk10Z9GoI9p/UxRJQ4pQthtemDU6EUQRh4EYG1WcxlkCz2URXpWuy7mFObLqAU7iD\\ngGm+IiECgYEA/DBOKvew6D1+JA+AOAnlk0k3jEX40tHVU9aoEuh2yyQ5fel+3snI\\nDaFmhGvnGyVePAuPQ/ADaWcWpqFM0AEdB66PLKs8VBNQ0hw2indojebZlEnKV6Ur\\nc4Wk7bSBkGOWsFy2Cs1xN+VN9b02KPUvOgoOi2Rm/Y0jJQUvZqai5xUCgYEA1+NJ\\ncXaJLyx5DFFNAMAC4fDr+La/9iG7glKtqHjLXIinfKyAwLqZ4ctt+xunwz9PXERo\\n9e5QsM7jlL5uLYivjhEx6TWacycyXCVCjE1cYyiXNhV9/3SZb/NIxO4ysPCeQga6\\nAooipa2s/IUT5zb4s6K7TINdPOOW9r/VS0Do8vUCgYEAoRoStWwpvRKbZFnqpOHd\\noKtjKt8AR1z4lGhKUlnimX74ozDodVYd0GdM4Ec2CadjfaQ8zz+iTlEmrSfZs/8i\\nFmgy2mxBS8xTEwYm6WnChvP0BsDk2/yNt2ymoZtwMVcNSnjPajM3omd/1/4ZfSy0\\nELWf+PgYutzQmLOpRkApTMkCgYBRo3qvdILWGvw/gzMaWIH+jQu/BuS6n/D3jGpt\\nLhjBClBD3jvmJepxL2uMrN2ZAQTywE/syE0tP19ibUze3TR+BdSY+xNH/oeVvuVW\\nhx6rxLrB0gjOpHotkpNvHSCANs2x7DdFJJWLj4y+BVkMc4ZC8APiID8O+oWpE8wF\\n5CrzTQKBgC+wDsFVXfQCQJ/38uZ+bwwr4Iv0KtT4qynuhb8v3wPVXoVztNBk7elS\\nTBEl85CYSm4/g1TNQhXHjRu2qZIya5AL+m9anPT/JXLkLX7LH17ba6KR3AcDrMNB\\n6YldSOrsEn+utd5Ahwh3aM/34nuYVMiBJT05zeEL3U/KZBGM+eSb\\n-----END RSA PRIVATE KEY-----\\n", "lsync_pub": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDTVQ1A1RdEyZdUgdBwhz7tWin8nOrZOvhYP5g2N3bgPb/a7PBTLn8VaCrKGfEPb5AJRfagAkFYE0Q2NpTE3oC6Fa7v+ITj6qSVWw5y1peHaRDAzwzh2Do1JBcaiyqB9ve43m4untQE7uqPbVJM/TKfWXfc7lnwI0B9CXcaNgRZ9mThACEBvNqXKN7OZNTIfLIG3us0G2Qg/sKT6Rcj8DA9lzw/a3RpMWQCrN0fnImXdmK44dVHLFVdItTFrsu9nt1IIV1RTF9LAmcggTPsrDbCCVIUuZadzn9vV1b+G0c8YWR1HuElM6Rwp5wkNF5t8vyTlq3l7NrDDsYENFm0b0uH Generated-by-Nova\\n", "wp_auth": "505462F3CC71C01DD587B165FD86783E", "version": "3.9.2", "chef_version": "11.16.2", "username": "wp_user", "wp_web_server_flavor": "2 GB General Purpose v1", "varnish_master_backend": "10.176.197.145", "parent_stack_id": "5cdde045-9767-46de-ab03-a8066725d5d4", "wp_logged_in": "1B9E401F9333F0829E8776756C8FFC9F", "kitchen": "https://github.com/rackspace-orchestration-templates/wordpress-multi", "wp_secure_auth": "2216EB44D671D2731BBAB2984AFD3BEE", "ssh_keypair_name": "5cdde045-9767-46de-ab03-a8066725d5d4", "database_name": "wordpress", "wp_web_server_hostname": "WordPress-Web0", "ssh_public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDUrHjU8oFe3KvXkf0vRznBhz171k5yhBTXTUIeR4Af8CP5Rys1ltFa5svzKEuixs2qUmrg99Zmg7hGDrEE9wea67xPLtOBgsePFt19sFw38mL2QCDFGGAtgiiPjrJj/01i5BW4Fhd7aFicpmVZqDb9daia4M+2Mz8vZm9WZ3yQizFSKeXD47fsRe1ZdzdhWjJqTG1QtJGNDR9w1beFpJeaZR36VaPq1VemitzHTTeuZ3tnJWAIPJiHLtzGVkFA2jglYhm+cqflHEdQIBVO051M0X54V9TF0w++cGUlRuNnDKNUAUVVetkpSqcF+etGjr9q5r7O/CFSzOYeUFEjYQEZ Generated-by-Nova\\n", "database_password": "b5tlz5ZfgnqItOZw", "database_host": "10.176.197.160"}}}}, "action": "CREATE", "project_id": "897502", "id": "22d99b64-0887-4ac6-b064-e6cd73129606", "resources": {"0": {"status": "COMPLETE", "name": "ADOPT_98324-wp_web_servers-nmyzh5ebxqjk-0-hguo7gb3olzk", "stack_user_project_id": "897502", "environment": {"parameter_defaults": {}, "parameters": {"domain": "example.com", "image": "Ubuntu 12.04 LTS (Precise Pangolin) (PVHVM)", "wp_auth": "505462F3CC71C01DD587B165FD86783E", "parent_stack_id": "5cdde045-9767-46de-ab03-a8066725d5d4", "prefix": "wp_", "ssh_private_key": "-----BEGIN RSA PRIVATE KEY-----\\nMIIEowIBAAKCAQEA1Kx41PKBXtyr15H9L0c5wYc9e9ZOcoQU101CHkeAH/Aj+Ucr\\nNZbRWubL8yhLosbNqlJq4PfWZoO4Rg6xBPcHmuu8Ty7TgYLHjxbdfbBcN/Ji9kAg\\nxRhgLYIoj46yY/9NYuQVuBYXe2hYnKZlWag2/XWomuDPtjM/L2ZvVmd8kIsxUinl\\nw+O37EXtWXc3YVoyakxtULSRjQ0fcNW3haSXmmUd+lWj6tVXporcx003rmd7ZyVg\\nCDyYhy7cxlZBQNo4JWIZvnKn5RxHUCAVTtOdTNF+eFfUxdMPvnBlJUbjZwyjVAFF\\nVXrZKUqnBfnrRo6/aua+zvwhUszmHlBRI2EBGQIDAQABAoIBADY2aO7Pio7l7aAc\\nBNBCdcSRdujUblbeuHlRpmMVkuGRU3o93BPjCCcF4kNvqCgsSUz7iWcjhjHHrfed\\n0x4S4otpQC1nIF9JORmOmJNrm3ZfgT6IhlH3rryrCy/dDjhTYiStQ6QTbZT1unDk\\nMb2zFaFylrI0UH5/fcHVeNgrtSMbAPvsSmldvh65d45jtxRf1/wo0WBnNHF7rypc\\nw6d6uFFxd5wiGSkMjir4A7k2Coiyq+LCjZHtRBXrNqFzPsWw4g7KBrQ9Af463JpR\\nk10Z9GoI9p/UxRJQ4pQthtemDU6EUQRh4EYG1WcxlkCz2URXpWuy7mFObLqAU7iD\\ngGm+IiECgYEA/DBOKvew6D1+JA+AOAnlk0k3jEX40tHVU9aoEuh2yyQ5fel+3snI\\nDaFmhGvnGyVePAuPQ/ADaWcWpqFM0AEdB66PLKs8VBNQ0hw2indojebZlEnKV6Ur\\nc4Wk7bSBkGOWsFy2Cs1xN+VN9b02KPUvOgoOi2Rm/Y0jJQUvZqai5xUCgYEA1+NJ\\ncXaJLyx5DFFNAMAC4fDr+La/9iG7glKtqHjLXIinfKyAwLqZ4ctt+xunwz9PXERo\\n9e5QsM7jlL5uLYivjhEx6TWacycyXCVCjE1cYyiXNhV9/3SZb/NIxO4ysPCeQga6\\nAooipa2s/IUT5zb4s6K7TINdPOOW9r/VS0Do8vUCgYEAoRoStWwpvRKbZFnqpOHd\\noKtjKt8AR1z4lGhKUlnimX74ozDodVYd0GdM4Ec2CadjfaQ8zz+iTlEmrSfZs/8i\\nFmgy2mxBS8xTEwYm6WnChvP0BsDk2/yNt2ymoZtwMVcNSnjPajM3omd/1/4ZfSy0\\nELWf+PgYutzQmLOpRkApTMkCgYBRo3qvdILWGvw/gzMaWIH+jQu/BuS6n/D3jGpt\\nLhjBClBD3jvmJepxL2uMrN2ZAQTywE/syE0tP19ibUze3TR+BdSY+xNH/oeVvuVW\\nhx6rxLrB0gjOpHotkpNvHSCANs2x7DdFJJWLj4y+BVkMc4ZC8APiID8O+oWpE8wF\\n5CrzTQKBgC+wDsFVXfQCQJ/38uZ+bwwr4Iv0KtT4qynuhb8v3wPVXoVztNBk7elS\\nTBEl85CYSm4/g1TNQhXHjRu2qZIya5AL+m9anPT/JXLkLX7LH17ba6KR3AcDrMNB\\n6YldSOrsEn+utd5Ahwh3aM/34nuYVMiBJT05zeEL3U/KZBGM+eSb\\n-----END RSA PRIVATE KEY-----\\n", "lsync_pub": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDTVQ1A1RdEyZdUgdBwhz7tWin8nOrZOvhYP5g2N3bgPb/a7PBTLn8VaCrKGfEPb5AJRfagAkFYE0Q2NpTE3oC6Fa7v+ITj6qSVWw5y1peHaRDAzwzh2Do1JBcaiyqB9ve43m4untQE7uqPbVJM/TKfWXfc7lnwI0B9CXcaNgRZ9mThACEBvNqXKN7OZNTIfLIG3us0G2Qg/sKT6Rcj8DA9lzw/a3RpMWQCrN0fnImXdmK44dVHLFVdItTFrsu9nt1IIV1RTF9LAmcggTPsrDbCCVIUuZadzn9vV1b+G0c8YWR1HuElM6Rwp5wkNF5t8vyTlq3l7NrDDsYENFm0b0uH Generated-by-Nova\\n", "wp_nonce": "E6E16A60BCE928B173C2E68BCAD8DA46", "version": "3.9.2", "chef_version": "11.16.2", "username": "wp_user", "wp_web_server_flavor": "2 GB General Purpose v1", "varnish_master_backend": "10.176.197.145", "memcached_host": "10.176.197.160", "wp_logged_in": "1B9E401F9333F0829E8776756C8FFC9F", "kitchen": "https://github.com/rackspace-orchestration-templates/wordpress-multi", "wp_secure_auth": "2216EB44D671D2731BBAB2984AFD3BEE", "ssh_keypair_name": "5cdde045-9767-46de-ab03-a8066725d5d4", "database_name": "wordpress", "wp_web_server_hostname": "WordPress-Web0", "ssh_public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDUrHjU8oFe3KvXkf0vRznBhz171k5yhBTXTUIeR4Af8CP5Rys1ltFa5svzKEuixs2qUmrg99Zmg7hGDrEE9wea67xPLtOBgsePFt19sFw38mL2QCDFGGAtgiiPjrJj/01i5BW4Fhd7aFicpmVZqDb9daia4M+2Mz8vZm9WZ3yQizFSKeXD47fsRe1ZdzdhWjJqTG1QtJGNDR9w1beFpJeaZR36VaPq1VemitzHTTeuZ3tnJWAIPJiHLtzGVkFA2jglYhm+cqflHEdQIBVO051M0X54V9TF0w++cGUlRuNnDKNUAUVVetkpSqcF+etGjr9q5r7O/CFSzOYeUFEjYQEZ Generated-by-Nova\\n", "database_password": "b5tlz5ZfgnqItOZw", "database_host": "10.176.197.160"}, "resource_registry": {"resources": {}, "https://raw.githubusercontent.com/rackspace-orchestration-templates/wordpress-multi/master/wordpress-web-server.yaml": "https://raw.githubusercontent.com/rackspace-orchestration-templates/wordpress-multi/master/wordpress-web-server.yaml"}}, "template": {"outputs": {"accessIPv4": {"value": {"get_attr": ["wp_web_server", "accessIPv4"]}}, "privateIPv4": {"value": {"get_attr": ["wp_web_server", "privateIPv4"]}}}, "heat_template_version": "2013-05-23", "description": "This is a Heat template to deploy a single Linux server running a WordPress.\\n", "parameters": {"domain": {"default": "example.com", "type": "string", "description": "Domain to be used with WordPress site"}, "image": {"default": "Ubuntu 12.04 LTS (Precise Pangolin) (PVHVM)", "type": "string", "description": "Server Image used for all servers.", "constraints": [{"description": "Must be a supported operating system.", "allowed_values": ["Ubuntu 12.04 LTS (Precise Pangolin) (PVHVM)"]}]}, "wp_nonce": {"type": "string"}, "memcached_host": {"default": "127.0.0.1", "type": "string", "description": "IP/Host of the memcached server"}, "prefix": {"default": "wp_", "type": "string", "description": "Prefix to use for"}, "ssh_private_key": {"type": "string"}, "lsync_pub": {"type": "string", "description": "Public key for lsync configuration", "constraints": null}, "wp_auth": {"type": "string"}, "version": {"default": "3.9.1", "type": "string", "description": "Version of WordPress to install"}, "chef_version": {"default": "11.16.2", "type": "string", "description": "Version of chef client to use"}, "username": {"default": "wp_user", "type": "string", "description": "Username for system, database, and WordPress logins."}, "wp_web_server_flavor": {"default": "2 GB General Purpose v1", "type": "string", "description": "Web Cloud Server flavor", "constraints": [{"description": "Must be a valid Rackspace Cloud Server flavor for the region you have\\nselected to deploy into.\\n", "allowed_values": ["1 GB General Purpose v1", "2 GB General Purpose v1", "4 GB General Purpose v1", "8 GB General Purpose v1", "15 GB I/O v1", "30 GB I/O v1", "1GB Standard Instance", "2GB Standard Instance", "4GB Standard Instance", "8GB Standard Instance", "15GB Standard Instance", "30GB Standard Instance"]}]}, "varnish_master_backend": {"default": "localhost", "type": "string", "description": "Master backend host for admin calls in Varnish"}, "parent_stack_id": {"default": "none", "type": "string", "description": "Stack id of the parent stack"}, "wp_logged_in": {"type": "string"}, "kitchen": {"default": "https://github.com/rackspace-orchestration-templates/wordpress-multi", "type": "string", "description": "URL for the kitchen to use"}, "wp_secure_auth": {"type": "string"}, "ssh_keypair_name": {"type": "string", "description": "keypair name to register with Nova for the root SSH key"}, "database_name": {"default": "wordpress", "type": "string", "description": "WordPress database name"}, "wp_web_server_hostname": {"default": "WordPress-Web", "type": "string", "description": "WordPress Web Server Name", "constraints": [{"length": {"max": 64, "min": 1}}, {"allowed_pattern": "^[a-zA-Z][a-zA-Z0-9-]*$", "description": "Must begin with a letter and contain only alphanumeric characters.\\n"}]}, "ssh_public_key": {"type": "string"}, "database_password": {"type": "string", "description": "Password to use for database connections."}, "database_host": {"default": "127.0.0.1", "type": "string", "description": "IP/Host of the database server"}}, "resources": {"wp_web_server_setup": {"depends_on": "wp_web_server", "type": "OS::Heat::ChefSolo", "properties": {"username": "root", "node": {"apache": {"listen_ports": [8080], "serversignature": "Off", "traceenable": "Off", "timeout": 30}, "varnish": {"version": "3.0", "listen_port": "80"}, "wordpress": {"keys": {"logged_in": {"get_param": "wp_logged_in"}, "secure_auth_key": {"get_param": "wp_secure_auth"}, "nonce_key": {"get_param": "wp_nonce"}, "auth": {"get_param": "wp_auth"}}, "server_aliases": [{"get_param": "domain"}], "version": {"get_param": "version"}, "db": {"host": {"get_param": "database_host"}, "pass": {"get_param": "database_password"}, "user": {"get_param": "username"}, "name": {"get_param": "database_name"}}, "dir": {"str_replace": {"params": {"%domain%": {"get_param": "domain"}}, "template": "/var/www/vhosts/%domain%"}}}, "run_list": ["recipe[apt]", "recipe[build-essential]", "recipe[rax-wordpress::apache-prep]", "recipe[rax-wordpress::x509]", "recipe[php]", "recipe[rax-install-packages]", "recipe[wordpress]", "recipe[rax-wordpress::user]", "recipe[rax-wordpress::memcache]", "recipe[varnish::repo]", "recipe[varnish]", "recipe[rax-wordpress::apache]", "recipe[rax-wordpress::varnish]", "recipe[rax-wordpress::firewall]", "recipe[rax-wordpress::lsyncd-client]"], "rax": {"varnish": {"master_backend": {"get_param": "varnish_master_backend"}}, "lsyncd": {"ssh": {"pub": {"get_param": "lsync_pub"}}}, "memcache": {"server": {"get_param": "memcached_host"}}, "wordpress": {"admin_pass": {"get_param": "database_password"}, "user": {"group": {"get_param": "username"}, "name": {"get_param": "username"}}}, "apache": {"domain": {"get_param": "domain"}}, "packages": ["php5-imagick"]}}, "private_key": {"get_param": "ssh_private_key"}, "host": {"get_attr": ["wp_web_server", "accessIPv4"]}, "chef_version": {"get_param": "chef_version"}, "kitchen": {"get_param": "kitchen"}}}, "wp_web_server": {"type": "Rackspace::Cloud::Server", "properties": {"key_name": {"get_param": "ssh_keypair_name"}, "flavor": {"get_param": "wp_web_server_flavor"}, "name": {"get_param": "wp_web_server_hostname"}, "image": {"get_param": "image"}, "metadata": {"rax-heat": {"get_param": "parent_stack_id"}}}}}}, "action": "CREATE", "project_id": "897502", "id": "6134176b-9323-4c5f-a2b4-fcbe4247a45a", "resources": {"wp_web_server_setup": {"status": "COMPLETE", "name": "wp_web_server_setup", "resource_data": {"process_id": "10930"}, "resource_id": "7e50edd2-d9c1-4b32-95c6-7f42cc0f2fa5", "action": "CREATE", "type": "OS::Heat::ChefSolo", "metadata": {}}, "wp_web_server": {"status": "COMPLETE", "name": "wp_web_server", "resource_data": {"private_key": "-----BEGIN RSA PRIVATE KEY-----\\nMIICXAIBAAKBgQCR0v1FW8Sgn/zwFXAz5qV9ru0KgRYKtBPW9K1A50czATT8FQaE\\n9vMPVBdiINGpNqGw31QEJG7q2eiSu2fh6SxP7FYlGB9zKkOfK7RQr4qK8uthI3ee\\n4RHE7gu1/WpoRLH05EioS6ysxXwdMwU/9VYfV9pgRBWuT+095I3OFw5KNwIDAQAB\\nAoGAJpra3i/LQFLanZyvVa4sBbf3nR5LfY3q6q9f5pzT5pbdNhdC4JSYCGjUv++8\\nUbXa3H5jOa2Dh70kqyPd/prCVgfdu57vK0XdhuoxRdQRwTKnZKoDGL0AS8r2pQzJ\\nLbHKPgj46AJCCn/7sV+ruVQsK8Z/m8zoLyNI/CUzHBaPweECQQC2i2Nc6cDntC+I\\n9eNVpXyfE/mRYRWha0OAo8W68Ts01JLiQY448/XL+IiSLWm+/HpaYj+DRY8YmH/X\\nERD0FDSZAkEAzIDmjM7o3i9H3DoLari+HPGmK5pgSYViL+aJXcvbL8ut62EugaYz\\nY4p3RnABaqZA4cxBvONrvl4L5ccV0bznTwJBAJ1A3Lso37Z7IcwBzvJ0GjRMF91m\\nXiTta3xBGVBfCZsMWPCyepuThjZNhxEuL/+ILrr4EjC61nfgv5h9KjapxVkCQHY/\\nppAO6DnpLu0ZpxZboppL5GDcEAcTGFZIQG+6+4+kf3lWJTUUbCyHmTZid386iNPH\\nbs+Q1PErokeIGYbAayMCQHS+pmhUDpRD/tX9QscDjrJibUMVcdZpVzrhCKfrlyiK\\nUoXCxlUz4E0NWxRapVkecC3HkCFmuckEdRu0IDEucEI=\\n-----END RSA PRIVATE KEY-----"}, "resource_id": "6e26e3a3-eb55-4285-8cd4-79206a359ef0", "action": "CREATE", "type": "Rackspace::Cloud::Server", "metadata": {}}}}}}, "wp_secure_auth": {"status": "COMPLETE", "name": "wp_secure_auth", "resource_data": {"value": "2216EB44D671D2731BBAB2984AFD3BEE"}, "resource_id": "ADOPT_98324-wp_secure_auth-xwza4n6mmm77", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}, "mysql_root_password": {"status": "COMPLETE", "name": "mysql_root_password", "resource_data": {"value": "zeSsquuwwdxI6dr5"}, "resource_id": "ADOPT_98324-mysql_root_password-agsw3mg4eaoc", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}, "mysql_debian_password": {"status": "COMPLETE", "name": "mysql_debian_password", "resource_data": {"value": "oMeqCl3H7A951PEx"}, "resource_id": "ADOPT_98324-mysql_debian_password-u2lbz234o2zs", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}, "wp_auth": {"status": "COMPLETE", "name": "wp_auth", "resource_data": {"value": "505462F3CC71C01DD587B165FD86783E"}, "resource_id": "ADOPT_98324-wp_auth-meqrqwgii7zr", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}, "ssh_key": {"status": "COMPLETE", "name": "ssh_key", "resource_data": {"private_key": "-----BEGIN RSA PRIVATE KEY-----\\nMIIEowIBAAKCAQEA1Kx41PKBXtyr15H9L0c5wYc9e9ZOcoQU101CHkeAH/Aj+Ucr\\nNZbRWubL8yhLosbNqlJq4PfWZoO4Rg6xBPcHmuu8Ty7TgYLHjxbdfbBcN/Ji9kAg\\nxRhgLYIoj46yY/9NYuQVuBYXe2hYnKZlWag2/XWomuDPtjM/L2ZvVmd8kIsxUinl\\nw+O37EXtWXc3YVoyakxtULSRjQ0fcNW3haSXmmUd+lWj6tVXporcx003rmd7ZyVg\\nCDyYhy7cxlZBQNo4JWIZvnKn5RxHUCAVTtOdTNF+eFfUxdMPvnBlJUbjZwyjVAFF\\nVXrZKUqnBfnrRo6/aua+zvwhUszmHlBRI2EBGQIDAQABAoIBADY2aO7Pio7l7aAc\\nBNBCdcSRdujUblbeuHlRpmMVkuGRU3o93BPjCCcF4kNvqCgsSUz7iWcjhjHHrfed\\n0x4S4otpQC1nIF9JORmOmJNrm3ZfgT6IhlH3rryrCy/dDjhTYiStQ6QTbZT1unDk\\nMb2zFaFylrI0UH5/fcHVeNgrtSMbAPvsSmldvh65d45jtxRf1/wo0WBnNHF7rypc\\nw6d6uFFxd5wiGSkMjir4A7k2Coiyq+LCjZHtRBXrNqFzPsWw4g7KBrQ9Af463JpR\\nk10Z9GoI9p/UxRJQ4pQthtemDU6EUQRh4EYG1WcxlkCz2URXpWuy7mFObLqAU7iD\\ngGm+IiECgYEA/DBOKvew6D1+JA+AOAnlk0k3jEX40tHVU9aoEuh2yyQ5fel+3snI\\nDaFmhGvnGyVePAuPQ/ADaWcWpqFM0AEdB66PLKs8VBNQ0hw2indojebZlEnKV6Ur\\nc4Wk7bSBkGOWsFy2Cs1xN+VN9b02KPUvOgoOi2Rm/Y0jJQUvZqai5xUCgYEA1+NJ\\ncXaJLyx5DFFNAMAC4fDr+La/9iG7glKtqHjLXIinfKyAwLqZ4ctt+xunwz9PXERo\\n9e5QsM7jlL5uLYivjhEx6TWacycyXCVCjE1cYyiXNhV9/3SZb/NIxO4ysPCeQga6\\nAooipa2s/IUT5zb4s6K7TINdPOOW9r/VS0Do8vUCgYEAoRoStWwpvRKbZFnqpOHd\\noKtjKt8AR1z4lGhKUlnimX74ozDodVYd0GdM4Ec2CadjfaQ8zz+iTlEmrSfZs/8i\\nFmgy2mxBS8xTEwYm6WnChvP0BsDk2/yNt2ymoZtwMVcNSnjPajM3omd/1/4ZfSy0\\nELWf+PgYutzQmLOpRkApTMkCgYBRo3qvdILWGvw/gzMaWIH+jQu/BuS6n/D3jGpt\\nLhjBClBD3jvmJepxL2uMrN2ZAQTywE/syE0tP19ibUze3TR+BdSY+xNH/oeVvuVW\\nhx6rxLrB0gjOpHotkpNvHSCANs2x7DdFJJWLj4y+BVkMc4ZC8APiID8O+oWpE8wF\\n5CrzTQKBgC+wDsFVXfQCQJ/38uZ+bwwr4Iv0KtT4qynuhb8v3wPVXoVztNBk7elS\\nTBEl85CYSm4/g1TNQhXHjRu2qZIya5AL+m9anPT/JXLkLX7LH17ba6KR3AcDrMNB\\n6YldSOrsEn+utd5Ahwh3aM/34nuYVMiBJT05zeEL3U/KZBGM+eSb\\n-----END RSA PRIVATE KEY-----\\n"}, "resource_id": "5cdde045-9767-46de-ab03-a8066725d5d4", "action": "CREATE", "type": "OS::Nova::KeyPair", "metadata": {}}, "wp_master_server": {"status": "COMPLETE", "name": "wp_master_server", "resource_data": {"private_key": "-----BEGIN RSA PRIVATE KEY-----\\nMIICXAIBAAKBgQCx492mKsc0PRigaaLQ/oVspyepbXAEbC9hkNnBxOtEgeVqHiWu\\nmzpJfHeVk+fX/ud5/HkJexED1FL1zfUkAjajgis9n8/AaznAHv+3qI2VSuMJzmKX\\n2fHqBdhp6CsdAkNd68TcBgcyruZHkq8K9slp58BeKsxKpvlq0tZHwXavpwIDAQAB\\nAoGAIzMboM3GLSgJv3Qnq4Mxk5Zf2r6086sUlRG8hQMaKqwpYR4mBq7gkbn3T7m8\\nnpjp5NF4gc/ARim1YL4oS7/EX7E3NC/UwO6zSnitlIYzE/yBDNNEHvdIeqhZt1fP\\nhXAGyvot7n1rWp+79cOCOqr2ZgzdAHkBrQE7Tb+6TSzUfUECQQC77xwnAvcjSEcC\\nZORCpnw8nvuaRspfXiCSbkVosZxIEJUUUnn0tSccnGkra/Q+5k1GF3nn+K+VkM5a\\nGo4ZG5krAkEA8lGAkCeUTqaXq9f/s3PtAJWtd4ZcBRck39MDJSmlYBiq0PQvn2sn\\nnxvNrG8vuetN1yMFn3zI96kQzdrl5PeNdQJBAKrHr/qXjEPIs5auXmte5TkldBiP\\nSen+HHVUtchc1lr6jq7IAEFquV8bl8q4sFzUZdZTERnG+LBexdZFmWmhlb8CQFnG\\nCDNf9noNDjQEGh+J20xUJ6gYhw77vBWQP6INA8/OU7qGPP563Hr9+fzgVHY0zund\\nd7/Woz3dzPP3HSTu8eECQHkQOfXZ8L3LlSNpytMqJI9thc2fruEGUT6SYQQ+FqLM\\nP9B1LNSkYUWUleSjXPpkJwzwYa6tO6pznt0X15pfQ+0=\\n-----END RSA PRIVATE KEY-----"}, "resource_id": "f03a2553-d611-48b2-9b73-a5d343dbbee6", "action": "CREATE", "type": "Rackspace::Cloud::Server", "metadata": {}}, "database_server_firewall": {"status": "COMPLETE", "name": "database_server_firewall", "resource_data": {"process_id": "13813"}, "resource_id": "6f0a9129-cc02-45f5-8490-591e2a5982e1", "action": "CREATE", "type": "OS::Heat::ChefSolo", "metadata": {}}, "database_server_setup": {"status": "COMPLETE", "name": "database_server_setup", "resource_data": {"process_id": "10799"}, "resource_id": "b1b8d413-12e2-4bcd-ad39-8aad772e94e5", "action": "CREATE", "type": "OS::Heat::ChefSolo", "metadata": {}}, "wp_master_server_setup": {"status": "COMPLETE", "name": "wp_master_server_setup", "resource_data": {"process_id": "11131"}, "resource_id": "dba3d1a5-3e7c-469a-8845-fdc54cd6cfcb", "action": "CREATE", "type": "OS::Heat::ChefSolo", "metadata": {}}, "wp_logged_in": {"status": "COMPLETE", "name": "wp_logged_in", "resource_data": {"value": "1B9E401F9333F0829E8776756C8FFC9F"}, "resource_id": "ADOPT_98324-wp_logged_in-b24qsyi3uunc", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}, "mysql_repl_password": {"status": "COMPLETE", "name": "mysql_repl_password", "resource_data": {"value": "ev9saFHsIOGouxeN"}, "resource_id": "ADOPT_98324-mysql_repl_password-pkstv4hpfg3u", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}, "database_password": {"status": "COMPLETE", "name": "database_password", "resource_data": {"value": "b5tlz5ZfgnqItOZw"}, "resource_id": "ADOPT_98324-database_password-roujzxbp3i77", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}, "wp_nonce": {"status": "COMPLETE", "name": "wp_nonce", "resource_data": {"value": "E6E16A60BCE928B173C2E68BCAD8DA46"}, "resource_id": "ADOPT_98324-wp_nonce-gpwap4n7dkzq", "action": "CREATE", "type": "OS::Heat::RandomString", "metadata": {}}}}
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
                    asresp, asbody, = self.abandon_stack(abandonStackId,
                                                         abandonStackName, region)
                    self._check_resp(asresp, asbody, apiname)
                except BadStatusLine:
                    print "Delete stack did not work"

            apiname = "adopt stack"
            adopt_stack_name = "ADOPT_%s" %datetime.datetime.now().microsecond
            try:
                asresp, asbody, stack_identifier = self.adopt_stack(
                    adopt_stack_name, region, adopt_data3, yaml_template,
                    parameters)
                self._check_resp(asresp, asbody, apiname)
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