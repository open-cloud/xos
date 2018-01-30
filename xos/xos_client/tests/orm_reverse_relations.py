
# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# These are functional tests of ManyToMany relations. These tests need to be conducted end-to-end with a real
# API to verify that the client and server ends of the API are working with each other.

import random
import string
import sys
import unittest

orm = None

from xosapi import xos_grpc_client

SERVICE_1_NAME = "test_service_1"
SERVICEINSTANCE_1_NAME = "test_service_instance_1"

SERVICE_2_NAME = "test_service_2"
SERVICEINSTANCE_2_NAME = "test_service_instance_2"

class TestORMReverseRelations(unittest.TestCase):
    def setUp(self):
        pass

    def cleanup_models(self, cls, name):
        objs = cls.objects.filter(name=name)
        for obj in objs:
            obj.delete()


    def tearDown(self):
        self.cleanup_models(orm.ServiceInstance, SERVICEINSTANCE_1_NAME)
        self.cleanup_models(orm.ServiceInstance, SERVICEINSTANCE_2_NAME)
        self.cleanup_models(orm.Service, SERVICE_1_NAME)
        self.cleanup_models(orm.Service, SERVICE_2_NAME)

    def test_reverse_relations(self):
        service1 = orm.Service(name=SERVICE_1_NAME)
        service1.save()

        serviceinstance1 = orm.ServiceInstance(name=SERVICEINSTANCE_1_NAME, owner=service1)
        serviceinstance1.save()

        service2 = orm.Service(name=SERVICE_2_NAME)
        service2.save()

        serviceinstance2 = orm.ServiceInstance(name=SERVICEINSTANCE_2_NAME, owner=service2)
        serviceinstance2.save()

        link = orm.ServiceInstanceLink(provider_service_instance = serviceinstance1, subscriber_service_instance = serviceinstance2)
        link.save()

        si1_readback = orm.ServiceInstance.objects.get(id = serviceinstance1.id)
        si2_readback = orm.ServiceInstance.objects.get(id = serviceinstance2.id)

        self.assertEqual(si1_readback.provided_links.count(), 1)
        self.assertEqual(si2_readback.subscribed_links.count(), 1)

def test_callback():
    global orm

    orm = xos_grpc_client.coreclient.xos_orm

    sys.argv=sys.argv[:1]  # unittest gets mad about the orm command line arguments
    unittest.main()

xos_grpc_client.start_api_parseargs(test_callback)

