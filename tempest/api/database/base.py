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

import logging

from tempest import clients
import tempest.test


LOG = logging.getLogger(__name__)


class BaseDatabaseTest(tempest.test.BaseTestCase):

    @classmethod
    def setUpClass(cls):
        os = clients.DatabaseManager(interface=cls._interface)
        cls.flavors_client = os.flavors_client
        cls.flavor_ref = cls.config.database.flavor_ref
