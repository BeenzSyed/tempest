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

import json
from tempest import clients
from tempest.common.utils import data_utils
from tempest.openstack.common import log as logging
import tempest.test


LOG = logging.getLogger(__name__)


class BaseOrchestrationTest(tempest.test.BaseTestCase):
    """Base test case class for all Orchestration API tests."""

    @classmethod
    def setUpClass(cls):
        super(BaseOrchestrationTest, cls).setUpClass()

        dns = clients.DnsManager()
        cls.dns = dns
        backup = clients.BackupManager()
        cls.backup = backup

        os = clients.OrchestrationManager()
        cls.orchestration_cfg = os.config.orchestration
        cls.compute_cfg = os.config.compute
        if not os.config.service_available.heat:
            raise cls.skipException("Heat support is required")
        cls.build_timeout = cls.orchestration_cfg.build_timeout
        cls.build_interval = cls.orchestration_cfg.build_interval

        cls.os = os
        cls.orchestration_client = os.orchestration_client
        cls.servers_client = os.servers_client
        cls.keypairs_client = os.keypairs_client
        cls.network_client = os.network_client
        cls.database_client = os.database_client
        cls.dns_client = dns.dns_client
        cls.backup_client = backup.backup_client
        cls.loadbalancer_client = os.loadbalancer_client
        cls.stacks = []
        cls.keypairs = []
        cls.volume_client = os.volumes_client


    @classmethod
    def _get_default_network(cls):
        resp, networks = cls.network_client.list_networks()
        for net in networks['networks']:
            if net['name'] == cls.compute_cfg.fixed_network_name:
                return net

    @classmethod
    def _get_identity_admin_client(cls):
        """
        Returns an instance of the Identity Admin API client
        """
        os = clients.AdminManager(interface=cls._interface)
        admin_client = os.identity_client
        return admin_client

    @classmethod
    def _get_client_args(cls):

        return (
            cls.config,
            cls.config.identity.admin_username,
            cls.config.identity.admin_password,
            cls.config.identity.uri
        )

    @classmethod
    def create_stack(cls, stack_name, region, template_data, parameters={}):
        resp, body = cls.client.create_stack(
            stack_name,
            region,
            #template_url='https://raw.github.com/heat-ci/heat-templates/master/staging/wordpress-multi.template',
            template=template_data,
            parameters=parameters)
        #print "resp is %s" % resp
        if (resp['status'] == '200' or resp['status'] == '201'):
            stack_id = resp['location'].split('/')[-1]
            stack_identifier = '%s/%s' % (stack_name, stack_id)
            cls.stacks.append(stack_identifier)
            #print "create stack worked! The response is: %s" % resp['status']
            return resp, body, stack_identifier
        else:
            #print "create stack did not work. The response is: %s %s" % (resp['status'], body)
            return resp, body, 0

    @classmethod
    def adopt_stack(cls, stack_name, region, stack_adopt_data, template_data, parameters={}):
        resp, body = cls.client.adopt_stack(
            stack_name,
            region,
            stack_adopt_data,
            template=template_data,
            parameters=parameters)
        if (resp['status'] == '200' or resp['status'] == '201'):
            stack_id = resp['location'].split('/')[-1]
            stack_identifier = '%s/%s' % (stack_name, stack_id)
            cls.stacks.append(stack_identifier)
            #print "adopt stack worked! The response is: %s" % resp['status']
            return resp, body, stack_identifier
        else:
            #print "adopt stack did not work. The response is: %s %s" % (resp['status'], body)
            return resp, body, 0

    @classmethod
    def update_stack(cls, stack_identifier, stack_name, region, template_data, parameters={}):
        # parameters = {
        # #     'InstanceType': self.orchestration_cfg.instance_type,
        # #     'ImageId': self.orchestration_cfg.image_ref,
        #     'key_name': "sabeen"
        # }
        resp, body = cls.client.update_stack(
            stack_identifier,
            stack_name,
            region,
            #template_url='https://raw.github.com/heat-ci/heat-templates/master/staging/wordpress-multi.template',
            template=template_data,
            parameters=parameters)
        #print "resp is %s" % resp
        return resp, body

    @classmethod
    def abandon_stack(cls, stackid, stackname, region):
        resp, body = cls.orchestration_client.abandon_stack(stackid, stackname, region)
        return resp, body

    @classmethod
    def get_stack(cls, stackid, region):
        """Returns the details of a single stack."""
        resp, body = cls.client.get_stack(stackid, region)
        # url = "stacks/%s" % stackid
        # resp, body = self.get(url)
        if resp['status'] == '200':
            body = json.loads(body)
            return resp, body['stack']
        else:
            return resp, body

    @classmethod
    def delete_stack(cls,stackname, stackid, region):
        resp, body = cls.orchestration_client.delete_stack(stackname, stackid, region)
        return resp, body

    @classmethod
    def clear_stacks(cls):
        for stack_identifier in cls.stacks:
            try:
                cls.orchestration_client.delete_stack(stack_identifier)
            except Exception:
                pass

        for stack_identifier in cls.stacks:
            try:
                cls.orchestration_client.wait_for_stack_status(
                    stack_identifier, 'DELETE_COMPLETE')
            except Exception:
                pass

    @classmethod
    def _create_keypair(cls, name_start='keypair-heat-'):
        kp_name = data_utils.rand_name(name_start)
        resp, body = cls.keypairs_client.create_keypair(kp_name)
        cls.keypairs.append(kp_name)
        return body

    @classmethod
    def clear_keypairs(cls):
        for kp_name in cls.keypairs:
            try:
                cls.keypairs_client.delete_keypair(kp_name)
            except Exception:
                pass

    @classmethod
    def tearDownClass(cls):
        cls.clear_stacks()
        cls.clear_keypairs()
        super(BaseOrchestrationTest, cls).tearDownClass()

    @staticmethod
    def stack_output(stack, output_key):
        """Return a stack output value for a give key."""
        return next((o['output_value'] for o in stack['outputs']
                    if o['output_key'] == output_key), None)
