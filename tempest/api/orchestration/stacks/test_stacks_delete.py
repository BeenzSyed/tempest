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
from tempest.test import attr
import os
from subprocess import call
import requests
import json
import git
import yaml
import re
from tempest.common import rest_client
#from heatclient import Client
import pdb

LOG = logging.getLogger(__name__)


class StacksTestJSON(base.BaseOrchestrationTest):
    _interface = 'json'

    empty_template = "HeatTemplateFormatVersion: '2013-05-23'\n"

    @classmethod
    def setUpClass(cls):
        super(StacksTestJSON, cls).setUpClass()
        cls.client = cls.orchestration_client

        # if os.path.exists("tmp"):
        #     call(["rm", '-rf', 'tmp'])
        # os.mkdir("tmp")
        # os.chdir("tmp")
        #check if working in online mode
        # response_templates = \
        #     requests.get(
        #         "https://raw.github.com/heat-ci/heat-prod-templates/master/example/redis.template",
        #         timeout=3)
        #print response_templates.content
        #print type(response_templates.content)
        #yaml_template = yaml.safe_load(response_templates.content)
        # json_templates = json.loads(response_templates.content)
        # for bp in yaml_templates:
        #     gitUrl = bp["git_url"]
        #     #print ("Downloading %s" % gitUrl)
        #     git.Git().clone(gitUrl, "--progress")
        # cls.gitRepoDirNames = os.listdir(".")
        #cls.yaml_temp = yaml_template

    @attr(type='smoke')
    def test_stack_delete(self):
        #list stacks
        regions = ['DFW', 'ORD', 'IAD', 'SYD', 'HKG', 'dev', 'qa', 'staging']
        for region in regions:
            resp, stacks = self.client.list_stacks(region)
            #go through one stack at a time and delete
            for stack in stacks:
                if not (re.search('CREATE_*', stack['stack_name']) or re.search('ADOPT_*', stack['stack_name']) or re.search('UPDATE_*', stack['stack_name']) or re.search('DONOTDELETE*', stack['stack_name'])):
                    print stack['stack_name']
                    print stack['id']
                    resp = self.client.delete_stack(stack['stack_name'], stack['id'], region)
                    print resp

    @attr(type='smoke')
    def test_stack_list(self):
        #list stacks
        region = "Dev"
        resp, stacks = self.client.list_stacks(region)
        #go through one stack at a time and delete
        for stack in stacks:
            if not (re.search('CREATE_*', stack['stack_name']) or re.search('ADOPT_*', stack['stack_name']) or re.search('UPDATE_*', stack['stack_name']) or re.search('DONOTDELETE*', stack['stack_name'])):
                print stack['stack_name']
                print stack['id']
                #resp = self.client.delete_stack(stack['stack_name'], stack['id'], region)
                #print resp

    @attr(type='smoke')
    def test_limits(self):

        response_templates = \
                requests.get(
                    "https://raw.github.com/heat-ci/heat-templates/master/staging/wordpress-multi.template",
                    timeout=3)
        yaml_template = yaml.safe_load(response_templates.content)
        for i in range(10):
            stack_name = rand_name('heat')
            print stack_name
            # count how many stacks to start with
            resp, stacks = self.client.list_stacks()
            stack_count = len(stacks)
            print stack_count

            stack_identifier = self.create_stack(stack_name, yaml_template)
            print stack_identifier

    @attr(type='smoke')
    def test_stack_crud_no_resources(self):

        response_templates = \
            requests.get(
                "https://raw.github.com/heat-ci/heat-templates/master/staging/wordpress-multi.template",
                timeout=3)
        #print response_templates.content
        #print type(response_templates.content)
        yaml_template = yaml.safe_load(response_templates.content)

        stack_name = rand_name('heat')

        # count how many stacks to start with
        #resp, stacks = self.client.list_stacks()
        #print body
        #stack_count = len(body['stacks'])
        #print stack_count

        #print yaml_template
        # create the stack
        #stack_name = 'Beenz3Stack'
        #stack_identifier = self.create_stack(stack_name, self.empty_template)
        print "hi"
        #pdb.set_trace()
        stack_identifier = self.create_stack(stack_name, yaml_template)
        print stack_identifier
        stack_id = stack_identifier.split('/')[1]
        # wait for create complete (with no resources it should be instant)
        timetaken = self.client.wait_for_stack_status(stack_identifier, 'CREATE_COMPLETE')
        print "time taken for stack to deploy: %s" %timetaken
        # stack count will increment by 1
        resp, stacks = self.client.list_stacks()
        # self.assertEqual(stack_count + 1, len(body['stacks']),
        #                  'Expected stack count to increment by 1')
        list_ids = list([stack['id'] for stack in stacks])
        self.assertIn(stack_id, list_ids)
        print resp
        #print len(body['stacks'])

        # # fetch the stack
        # resp, stack = self.client.get_stack(stack_identifier)
        # self.assertEqual('CREATE_COMPLETE', stack['stack_status'])
        #
        # # fetch the stack by name
        # resp, stack = self.client.get_stack(stack_name)
        # self.assertEqual('CREATE_COMPLETE', stack['stack_status'])
        #
        # # fetch the stack by id
        # resp, stack = self.client.get_stack(stack_id)
        # self.assertEqual('CREATE_COMPLETE', stack['stack_status'])

        # delete the stack
        #resp = self.client.delete_stack(stack_identifier)
        #self.assertEqual('204', resp[0]['status'])
