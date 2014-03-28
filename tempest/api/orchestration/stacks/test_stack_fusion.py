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
import requests
import yaml
import time
import os
import re
import string
import pdb
import json



LOG = logging.getLogger(__name__)


class StacksTestJSON(base.BaseOrchestrationTest):
    _interface = 'json'

    @classmethod
    def setUpClass(cls):
        super(StacksTestJSON, cls).setUpClass()
        cls.client = cls.orchestration_client

    # def test_supported_template(self):
    #     self._create_stack("wp-resource")

    def test_get_template_catalog(self):
        region = "IAD"
        resp , body = self.orchestration_client.get_template_catalog(region)
        self.assertEqual(resp['status'], '200')

    def test_get_single_template(self):
        region = "IAD"
        template_id="15901104"
        resp , body = self.orchestration_client.get_single_template(
            template_id,region)
        self.assertEqual(resp['status'], '200')

    def test_get_list_of_stacks(self):
        region = "IAD"
        resp , body = self.orchestration_client.get_list_of_stacks_fusion(region)
        print resp , body
        self.assertEqual(resp['status'], '200')


    def test_create_stack_with_supported_template_id(self):
        template_id = "SHWETA"
        region = "IAD"
        stack_name = rand_name("qe_"+template_id+region)
        resp,body = self.orchestration_client.create_stack_fusion(
            stack_name,region,template_id)
        print resp, body

        self.assertEqual(resp['status'], '200')


    def test_create_stack_with_supported_template(self):
        template_giturl = "https://raw.github" \
                          ".com/heat-ci/heat-templates/master/qa/rcbops_allinone_inone" \
                          ".template"
        region = "IAD"
        # resp , body = self.orchestration_client.get_template_catalog(region)
        # for template in body['templates']:
        #     if template['id'] == "rcbops_allinone_inone":
        #         template = json.loads(template)
        #        # yaml_template = yaml.safe_load(template.content)
        #         print "done"
        #
        #
        # self.assertEqual(resp['status'], '200')

        response_templates = requests.get(template_giturl, timeout=10)
        if response_templates.status_code != requests.codes.ok:
            print "This template does not exist: %s" % template_giturl
            self.fail("The template does not exist.")
        else:
            yaml_template = yaml.safe_load(response_templates.content)

        #template_id = "15901104"
        region = "IAD"
        parameters = {}
        stack_name = rand_name("qe_")
       # resp,body = self.orchestration_client.create_stack_fusion(
         #   stack_name,region,template_id)
        resp,body =self.orchestration_client.create_stack_fusion(stack_name, region,
                                              template_id=None,
                                                template=yaml_template,
                                                parameters=parameters)
        print resp, body
        self.assertEqual(resp['status'], '200')

