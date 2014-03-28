# Copyright 2012 OpenStack, LLC
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

from tempest.common.rest_client import RestClient


class DatabaseClient(RestClient):
    def __init__(self,
                 config,
                 username,
                 password,
                 auth_url,token_url,
                 tenant_name=None):
        super(DatabaseClient, self).__init__(config,
                                             username,
                                             password,
                                             auth_url,token_url,
                                             tenant_name)
        self.service = self.config.database.catalog_type

    def list_flavors(self):
        resp, body = self.get("flavors")
        body = json.loads(body)
        return resp, body['flavors']

    def get_instance(self, instanceId, region):
        url = "instances/%s" %instanceId
        resp, body = self.get(url,region)
        if resp['status']=='200':
             body = json.loads(body)
        return resp ,body