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

from tempest.api.database import base
from tempest import exceptions
from tempest.test import attr


class FlavorsTestJSON(base.BaseDatabaseTest):
    _interface = 'json'

    @classmethod
    def setUpClass(cls):
        super(FlavorsTestJSON, cls).setUpClass()
        cls.client = cls.flavors_client

    @attr(type='incubation')
    def test_list_flavors(self):
        # List of all flavors should contain the expected flavor
        resp, flavors = self.client.list_flavors()
        resp, flavor = self.client.get_flavor_details(self.flavor_ref)
        flavor_min_detail = {'ram': flavor['ram'],
                             'id': flavor['id'],
                             'links': flavor['links'],
                             'name': flavor['name']}
        self.assertTrue(flavor_min_detail in flavors)
