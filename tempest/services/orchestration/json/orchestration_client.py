# Copyright 2013 IBM Corp.
# All Rights Reserved.
#
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
import re
import time
import urllib
import datetime
import pdb

from tempest.common import rest_client
from tempest import exceptions


class OrchestrationClient(rest_client.RestClient):

    def __init__(self, config, username, password, auth_url, token_url,
                 tenant_name=None):
        super(OrchestrationClient, self).__init__(config, username, password,
                                                  auth_url, token_url,
                                                  tenant_name)
        self.service = self.config.orchestration.catalog_type
        self.build_interval = self.config.orchestration.build_interval
        self.build_timeout = self.config.orchestration.build_timeout

    def list_stacks(self, region, params=None):
        """Lists all stacks for a user."""

        uri = 'stacks'
        if params:
            uri += '?%s' % urllib.urlencode(params)
        resp, body = self.get(uri, region)
        if resp['status'] == '200':
            body = json.loads(body)
            return resp, body['stacks']
        else:
            return resp, body

    def list_stacks_mgmt_api(self, region, params=None):
        """Lists all stacks for a user."""

        # uri = 'stacks'
        # if params:
        #     uri += '?%s?GLOBAL_TENANT=1' % urllib.urlencode(params)
        # print uri

        url = "stacks?global_tenant=1"
        resp, body = self.get(url, region)
        if resp['status'] == '200':
            body = json.loads(body)
            return resp, body['stacks']
        else:
            return resp, body

    def create_stack(self, name, region, disable_rollback=True, parameters={},
                     timeout_mins=120, template=None, template_url=None):
        headers, body = self._prepare_update_create(
            name,
            disable_rollback,
            parameters,
            timeout_mins,
            template,
            template_url)
        uri = 'stacks'
        resp, body = self.post(uri, region, headers=headers, body=body)
        return resp, body

    def update_stack(self, stack_identifier, name, region, disable_rollback=True,
                     parameters={}, timeout_mins=60, template=None,
                     template_url=None):
        headers, body = self._prepare_update_create(
            name,
            disable_rollback,
            parameters,
            timeout_mins,
            template,
            template_url)

        uri = "stacks/%s/%s" % (name, stack_identifier)
        resp, body = self.put(uri, region, headers=headers, body=body)
        return resp, body

    def abandon_stack(self, stack_identifier, name, region, disable_rollback=True,
                     parameters={}, timeout_mins=60, template=None,
                     template_url=None):
        headers, body = self._prepare_update_create(
            name,
            disable_rollback,
            parameters,
            timeout_mins,
            template,
            template_url)
        uri = "stacks/%s/%s/" % (name, stack_identifier)
        resp, body = self.delete(uri, region, headers=headers)
        return resp, body

    def adopt_stack(self, name, region, adopt_stack_data,
                    disable_rollback=True, parameters={},
                     timeout_mins=120, template=None, template_url=None):
        # print "name is %s" % name
        # print "region is %s" % region
        # print "adopt stack data is %s" % adopt_stack_data
        # print "disable rollback is %s" % disable_rollback
        # print "parameters are %s" % parameters
        # print "template %s" % template
        # print "template url %s" % template_url
        disable_rollback = True
        headers, body = self._prepare_adopt(
            name,
            adopt_stack_data,
            disable_rollback,
            parameters,
            timeout_mins,
            template,
            template_url)
        uri = 'stacks'
        resp, body = self.post(uri, region, headers=headers, body=body)
        return resp, body

    # def abandon_stack(self, stack_name, stack_identifier, region):
    #     """Returns the details of a single resource."""
    #     url = "stacks/%s/%s/abandon" % (stack_name, stack_identifier)
    #     resp, body = self.delete(url, region)
    #     return resp, body

    def _prepare_update_create(self, name, disable_rollback=True,
                               parameters={}, timeout_mins=120,
                               template=None, template_url=None):
        post_body = {
            "stack_name": name,
            "disable_rollback": disable_rollback,
            "parameters": parameters,
            "timeout_mins": timeout_mins
            #"template": "HeatTemplateFormatVersion: '2013-05-23'\n"
        }
        if template:
            post_body['template'] = template
        if template_url:
            post_body['template_url'] = template_url
        body = json.dumps(post_body, default=datehandler)
        # uri = 'stacks'
        # resp, body = self.post(uri, headers=self.headers, body=body)
        # return resp, body

        # Password must be provided on stack create so that heat
        # can perform future operations on behalf of the user
        headers = dict(self.headers)
        headers['X-Auth-Key'] = self.password
        headers['X-Auth-User'] = self.user
        return headers, body

    def _prepare_adopt(self, name, adopt_stack_data, disable_rollback=True,
                               parameters={}, timeout_mins=120,
                               template=None, template_url=None):
        # print "stack name is %s" % name
        # print "adopt stack data is %s" % adopt_stack_data
        # print "rollback is %s" % disable_rollback
        # print "parameters are %s" % parameters
        # print "timeout is %s" % timeout_mins
        # print template
        # print template_url
        post_body = {
            "stack_name": name,
            "adopt_stack_data": adopt_stack_data,
            "disable_rollback": disable_rollback,
            "parameters": parameters,
            "timeout_mins": timeout_mins
            #"template": "HeatTemplateFormatVersion: '2013-05-23'\n"
        }
        if template:
            post_body['template'] = template
        if template_url:
            post_body['template_url'] = template_url
        body = json.dumps(post_body, default=datehandler)
        # uri = 'stacks'
        # resp, body = self.post(uri, headers=self.headers, body=body)
        # return resp, body

        # Password must be provided on stack create so that heat
        # can perform future operations on behalf of the user
        headers = dict(self.headers)
        headers['X-Auth-Key'] = self.password
        headers['X-Auth-User'] = self.user
        return headers, body

    def get_stack(self, stack_identifier, region):
        """Returns the details of a single stack."""
        url = "stacks/%s" % stack_identifier
        resp, body = self.get(url, region)
        return resp, body


    def get_stack_id(self, stack_name):
        """Returns the details of a single stack."""
        url = "stacks/%s" % stack_name
        resp, body = self.get(url)
        if resp['status'] == '200':
            body = json.loads(body)
            return resp, body['stack']
        else:
            return resp, body

    def suspend_stack(self, stack_identifier, region):
        """Suspend a stack."""
        url = 'stacks/%s/actions' % stack_identifier
        body = {'suspend': None}
        resp, body = self.post(url, region, json.dumps(body), self.headers)
        return resp, body

    def resume_stack(self, stack_identifier, region):
        """Resume a stack."""
        url = 'stacks/%s/actions' % stack_identifier
        body = {'resume': None}
        resp, body = self.post(url, region, json.dumps(body), self.headers)

    def get_api_version(self, region):
        """Returns api version with response."""
        url = "https://%s.orchestration.api.rackspacecloud" \
              ".com/versions/"%region
        resp, body = self.get(url,region)
        body = json.loads(body)
        return resp, body

    def get_build_info(self, region):
        url = "build_info"
        resp, body = self.get(url, region)
        body = json.loads(body)
        return resp, body

    def list_resources(self, stack_name, stack_identifier, region):
        """Returns the details of a single resource."""
        url = "stacks/%s/%s/resources" % (stack_name, stack_identifier)
        resp, body = self.get(url, region)
        if resp['status'] == '200':
            body = json.loads(body)
            return resp, body['resources']
        else:
            return resp, body

    def get_resource(self, stack_name, stack_identifier, resource_name, region):
        """Returns the details of a single resource."""
        url = "stacks/%s/%s/resources/%s" % (stack_name, stack_identifier, resource_name)
        resp, body = self.get(url, region)
        if resp['status'] == '200':
            body = json.loads(body)
            return resp, body['resource']
        else:
            return resp, body

    def delete_stack(self, stack_name, stack_id, region):
        """Deletes the specified Stack."""
        return self.delete("stacks/%s/%s" % (str(stack_name), str(stack_id)), region)

    def wait_for_resource_status(self, stack_identifier, resource_name,
                                 status, failure_pattern='^.*_FAILED$'):
        """Waits for a Resource to reach a given status."""
        start = int(time.time())
        fail_regexp = re.compile(failure_pattern)

        while True:
            try:
                resp, body = self.get_resource(
                    stack_identifier, resource_name)
            except exceptions.NotFound:
                # ignore this, as the resource may not have
                # been created yet
                pass
            else:
                resource_name = body['resource_name']
                resource_status = body['resource_status']
                if resource_status == status:
                    return
                if fail_regexp.search(resource_status):
                    raise exceptions.StackBuildErrorException(
                        stack_identifier=stack_identifier,
                        resource_status=resource_status,
                        resource_status_reason=body['resource_status_reason'])

            if int(time.time()) - start >= self.build_timeout:
                message = ('Resource %s failed to reach %s status within '
                           'the required time (%s s).' %
                           (resource_name, status, self.build_timeout))
                raise exceptions.TimeoutException(message)
            time.sleep(self.build_interval)

    def wait_for_stack_status(self, stack_identifier, status,
                              failure_pattern='^.*_FAILED$'):
        """Waits for a Stack to reach a given status."""
        start = int(time.time())
        fail_regexp = re.compile(failure_pattern)

        while True:
            resp, body = self.get_stack(stack_identifier)
            stack_name = body['stack_name']
            stack_status = body['stack_status']
            if stack_status == status:
                return
            if fail_regexp.search(stack_status):
                raise exceptions.StackBuildErrorException(
                    stack_identifier=stack_identifier,
                    stack_status=stack_status,
                    stack_status_reason=body['stack_status_reason'])
            print "timeout"
            print self.build_timeout
            if int(time.time()) - start >= self.build_timeout:
                message = ('Stack %s failed to reach %s status within '
                           'the required time (%s s).' %
                           (stack_name, status, self.build_timeout))
                raise exceptions.TimeoutException(message)
            time.sleep(self.build_interval)

    def show_resource_metadata(self, stack_name, stack_identifier, resource_name, region):
        """Returns the resource's metadata."""
        url = ('stacks/{stack_name}/{stack_identifier}/resources/{resource_name}'
               '/metadata'.format(**locals()))
        resp, body = self.get(url, region)
        if resp['status'] == '200':
            body = json.loads(body)
            return resp, body['metadata']
        else:
            return resp, body

    def list_events(self, stack_name, stack_identifier, region):
        """Returns list of all events for a stack."""
        url = 'stacks/{stack_name}/{stack_identifier}/events'.format(**locals())
        resp, body = self.get(url, region)
        if resp['status'] == '200':
            body = json.loads(body)
            return resp, body['events']
        else:
            return resp, body

    def list_resource_events(self, stack_identifier, resource_name):
        """Returns list of all events for a resource from stack."""
        url = ('stacks/{stack_identifier}/resources/{resource_name}'
               '/events'.format(**locals()))
        resp, body = self.get(url)
        if resp['status'] == '200':
            body = json.loads(body)
            return resp, body['events']
        else:
            return resp, body

    def show_event(self, stack_name, stack_identifier, resource_name, event_id, region):
        """Returns the details of a single stack's event."""
        url = ('stacks/{stack_name}/{stack_identifier}/resources/{resource_name}/events'
                '/{event_id}'.format(**locals()))
        #url = ('stacks/{stack_name}/{stack_identifier}/resources/{resource_name}/events'.format(**locals()))
        #print "url for show event %s" % url
        resp, body = self.get(url, region)
        if resp['status'] == '200':
            body = json.loads(body)
            return resp, body['event']
        else:
            return resp, body

    def show_template(self, stack_name, stack_identifier, region):
        """Returns the template for the stack."""
        url = ('stacks/{stack_name}/{stack_identifier}/template'.format(**locals()))
        resp, body = self.get(url, region)
        if resp['status'] == '200':
            body = json.loads(body)
        return resp, body

    def template_resource(self, region):
        """Lists the supported template resource types."""
        url = ('resource_types'.format(**locals()))
        resp, body = self.get(url, region)
        if resp['status'] == '200':
            body = json.loads(body)
        return resp, body

    def resource_schema(self, type_name, region):
        """Gets the interface schema for a specified resource type. """
        url = ('resource_types/{type_name}'.format(**locals()))
        resp, body = self.get(url, region)
        if resp['status'] == '200':
            body = json.loads(body)
        return resp, body

    def resource_template(self, type_name, region):
        """Returns the template for the stack."""
        url = ('resource_types/{type_name}/template'.format(**locals()))
        resp, body = self.get(url, region)
        if resp['status'] == '200':
            body = json.loads(body)
        return resp, body

    def show_stack(self, stack_name, stack_identifier, region):
        """Returns the parameters for the stack."""
        url = 'stacks/%s/%s' % (stack_name, stack_identifier)
        resp, body = self.get(url, region)
        if resp['status'] in('200','201'):
            body = json.loads(body)
        return resp, body

    def _validate_template(self, region, post_body):
        """Returns the validation request result."""
        post_body = json.dumps(post_body, default=datehandler)
        resp, body = self.post('validate', region, post_body, self.headers)
        if resp['status'] == '200':
            body = json.loads(body)
        return resp, body

    def validate_template(self, region, template, parameters={}):
        """Returns the validation result for a template with parameters."""
        post_body = {
            'template': template,
            'parameters': parameters,
        }
        return self._validate_template(region, post_body)

    def validate_template_url(self, template_url, parameters={}):
        """Returns the validation result for a template with parameters."""
        post_body = {
            'template_url': template_url,
            'parameters': parameters,
        }
        return self._validate_template(post_body)

    def validate_autoscale_response(self, url, region):
        """Returns the response for Autoscale url for the stack."""
        resp, body = self.post(url, region, body=None, headers=self.headers)
        return resp, body

    def get_template_catalog(self, region):

        """Returns the template_catalog from fusion."""
        url = "templates"

        resp, body = self.get(url, region)
        if resp['status'] == '200':
            body = json.loads(body)
        return resp, body

    def get_template_catalog_with_metadata(self, region):

        """Returns the template_catalog from fusion."""
        url = "templates?with_metadata=True"

        resp, body = self.get(url, region)
        if resp['status'] == '200':
            body = json.loads(body)
        return resp, body

    def get_single_template(self, template_id, region):

        """Returns the template from fusion for template_id."""
        url = "templates/%s" % template_id
        resp, body = self.get(url, region)
        if resp['status'] == '200':
            body = json.loads(body)
        return resp, body

    def get_single_template_with_metadata(self, template_id, region):

        """Returns the template from fusion for template_id."""
        url = "templates/%s?with_metadata=True" % template_id
        resp, body = self.get(url, region)
        if resp['status'] == '200':
            body = json.loads(body)
        return resp, body

    def get_list_of_stacks_fusion(self, region):

        """Returns the template from fusion for template_id."""
        url = "stacks"
        resp, body = self.get(url, region)
        return resp, body

    def _prepare_update_create_for_fusion(self, name,
                                          parameters={},
                                          template_id=None,
                                          template={}):
        post_body = {
            "stack_name": name,
            "parameters": parameters,
            "disable_rollback": True,
            "timeout_mins": "120"
        }
        if template_id:
            post_body['template_id'] = template_id
        if template:
            post_body['template'] = template
        body = json.dumps(post_body, default=datehandler)
        #print "This is the Request Body: %s" % body
        headers = dict(self.headers)
        headers['X-Auth-Key'] = self.password
        headers['X-Auth-User'] = self.user
        return headers, body

    def create_stack_fusion(self, name, region, template_id=None, template={},
                            parameters={}):
        headers, body = self._prepare_update_create_for_fusion(
            name, parameters=parameters,
            template_id=template_id, template=template)
        uri = 'stacks'
        resp, body = self.post(uri, region, headers=headers, body=body)
        if resp['status'] == '201':
            body = json.loads(body)
        return resp, body

    def get_stack_info_for_fusion(self, url, region):
        """Returns the template from fusion for template_id."""
       # url = "stacks"
        resp, body = self.get(url, region)
        if resp['status'] == '200':
            body = json.loads(body)
        return resp, body

    def stack_preview(self, name, region, template_id=None, template={},
                            parameters={}):
        headers, body = self._prepare_update_create_for_fusion(
            name, parameters=parameters,
            template_id=template_id, template=template)
        uri = 'stacks/preview'
        resp, body = self.post(uri, region, headers=headers, body=body)
        if resp['status'] == '200':
            body = json.loads(body)
        return resp, body

    def update_stack_fusion(self, stack_identifier, name, region,
                            template_id=None, template={},
                            parameters={}):
        headers, body = self._prepare_update_create_for_fusion(
            name, parameters=parameters,
            template_id=template_id, template=template)
        uri = "stacks/%s/%s" % (name, stack_identifier)
        resp, body = self.put(uri, region, headers=headers, body=body)
        return resp, body

    def store_stack_fusion(self, name, region, template_id=None, template={},
                            parameters={}):
        headers, body = self._prepare_update_create_for_fusion(
            name, parameters=parameters,
            template_id=template_id, template=template)
        uri = 'templates'
        resp, body = self.post(uri, region, headers=headers, body=body)
        if resp['status'] == '201':
            body = json.loads(body)
        return resp, body

    def update_template(self, template_id, new_template, region):

        container = "rackspace_orchestration_templates_store"
        heatqe_account_id = "862456"

        '''
        curl -i -X PUT -H 'X-Auth-Key: ****' -H 'X-Auth-User: heatdevunmanaged' -H 'User-Agent: python-heatclient'
        -H 'Content-Type: application/json' -H 'Accept: application/json' -H 'X-Auth-Token:  70cfb33cd43a41198aee10fbb239153c'
        -d '{"files": {}, "environment": {}, "template_name": "test_template_1", "template": {"heat_template_version": "2013-05-23",
        "description": "Simple template to deploy a single compute instance", "resources": {"my_instance": {"type": "OS::Nova::Server",
        "properties": {"key_name": "primkey", "image": "CentOS 6.5", "flavor": "m1.small"}}}}}' http://localhost:8008/v1/897686/templates/
        9cbc7fed518c9d507072e186f37868e8
        '''

        #container?!?!?
        uri = "%s/%s/%s" % heatqe_account_id, container, template_id

        headers = dict(self.headers)
        headers['X-Auth-User'] = self.user
        headers['X-Auth-Key'] = self.password
        headers['Content-Type'] = 'application/json'
        body = new_template

        resp, body = self.put(uri, region, body=body, headers=headers)
        if resp['status'] == '202':
            body = json.loads(body)
        return resp, body

    def delete_template(self, template_id, region):

        container = "rackspace_orchestration_templates_store"
        heatqe_account_id = "862456"

        '''
        curl -i -X DELETE -H 'X-Auth-Key: *****' -H 'X-Auth-User: heatdevunmanaged' -H 'Uer-Agent: python-heatclient'
        -H 'Content-Type: application/json' -H 'Accept: application/json' -H 'X-Auth-Token:70cfb33cd43a41198aee10fbb239153c'
        -k http://localhost:8008/v1/897686/templates/9cbc7fed518c9d507072e186f37868e8
        '''

        uri = "%s/%s/%s" % heatqe_account_id, container, template_id

        headers = dict(self.headers)
        headers['X-Auth-User'] = self.user
        headers['X-Auth-Key'] = self.password

        resp, body = self.delete(uri, region, headers=headers)
        if resp['status'] == '204':
            body = json.loads(body)
        return resp, body


def datehandler(obj):
    if isinstance(obj, datetime.date):
        return str(obj)
    else:
        raise TypeError, 'Object of type %s with value of %s is not ' \
                         'JSON serializable' % (type(obj), repr(obj))

