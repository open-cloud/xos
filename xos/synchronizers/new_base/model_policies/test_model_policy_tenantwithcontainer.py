
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


import unittest
from mock import patch
import mock
import pdb

import os, sys
sys.path.append("../../..")
sys.path.append("../../new_base/model_policies")
config = basic_conf = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + "/test_config.yaml")
from xosconfig import Config
Config.init(config, 'synchronizer-config-schema.yaml')

import synchronizers.new_base.modelaccessor

import model_policy_tenantwithcontainer
from model_policy_tenantwithcontainer import TenantWithContainerPolicy, LeastLoadedNodeScheduler

class MockObject:
    objects = None
    def __init__(self, **kwargs):
        for (k,v) in kwargs.items():
            setattr(self,k,v)
    def save(self):
        pass
    def delete(self):
        pass

class MockFlavor(MockObject):
    name = None

class MockInstance(MockObject):
    name = None

class MockDeployment(MockObject):
    name = None

class MockUser(MockObject):
    email = None

class MockSlice(MockObject):
    name = None

class MockNode(MockObject):
    hostname = None
    site_deployment = None

class MockImage(MockObject):
    name = None

class MockTenant(MockObject):
    owner = None
    deleted = False
    instance = None
    creator = None
    service_specific_attribute = {}

    def get_image(self):
        return None

class TestModelPolicyTenantWithContainer(unittest.TestCase):
    def setUp(self):
        self.policy = TenantWithContainerPolicy()
        self.user = MockUser(email="testadmin@test.org")
        self.tenant = MockTenant(creator=self.user)
        self.flavor = MockFlavor(name="m1.small")
        model_policy_tenantwithcontainer.Instance = MockInstance
        model_policy_tenantwithcontainer.Flavor = MockFlavor

    @patch.object(MockTenant, "owner")
    def test_manage_container_no_slices(self, owner):
        owner.slices.count.return_value = 0
        with self.assertRaises(Exception) as e:
            self.policy.manage_container(self.tenant)
        self.assertEqual(e.exception.message, "The service has no slices")

    @patch.object(MockTenant, "owner")
    @patch.object(MockTenant, "save")
    @patch.object(TenantWithContainerPolicy, "get_image")
    @patch.object(LeastLoadedNodeScheduler, "pick")
    @patch.object(MockNode, "site_deployment")
    @patch.object(MockInstance, "save")
    @patch.object(MockInstance, "delete")
    def test_manage_container(self, instance_delete, instance_save, site_deployment, pick, get_image, tenant_save, owner):
        # setup mocks
        node = MockNode(hostname="my.node.com")
        slice = MockSlice(name="mysite_test1", default_flavor=self.flavor, default_isolation="vm")
        image = MockImage(name="trusty-server-multi-nic")
        deployment = MockDeployment(name="testdeployment")
        owner.slices.count.return_value = 1
        owner.slices.all.return_value = [slice]
        owner.slices.first.return_value = slice
        get_image.return_value = image
        pick.return_value = (node, None)
        site_deployment.deployment = deployment
        # done setup mocks

        # call manage_container
        self.policy.manage_container(self.tenant)

        # make sure manage_container did what it is supposed to do
        self.assertNotEqual(self.tenant.instance, None)
        self.assertEqual(self.tenant.instance.creator.email, "testadmin@test.org")
        self.assertEqual(self.tenant.instance.image.name, "trusty-server-multi-nic")
        self.assertEqual(self.tenant.instance.flavor.name, "m1.small")
        self.assertEqual(self.tenant.instance.isolation, "vm")
        self.assertEqual(self.tenant.instance.node.hostname, "my.node.com")
        self.assertEqual(self.tenant.instance.slice.name, "mysite_test1")
        self.assertEqual(self.tenant.instance.parent, None)
        instance_save.assert_called()
        instance_delete.assert_not_called()
        tenant_save.assert_called()

    def test_manage_container_delete(self):
        self.tenant.deleted = True

        # call manage_container
        self.policy.manage_container(self.tenant)

        # make sure manage_container did what it is supposed to do
        self.assertEqual(self.tenant.instance, None)

    @patch.object(MockTenant, "owner")
    @patch.object(MockTenant, "save")
    @patch.object(TenantWithContainerPolicy, "get_image")
    @patch.object(LeastLoadedNodeScheduler, "pick")
    @patch.object(MockNode, "site_deployment")
    @patch.object(MockInstance, "save")
    @patch.object(MockInstance, "delete")
    @patch.object(MockFlavor, "objects")
    def test_manage_container_no_m1_small(self, flavor_objects, instance_delete, instance_save, site_deployment, pick, get_image, tenant_save, owner):
        # setup mocks
        node = MockNode(hostname="my.node.com")
        slice = MockSlice(name="mysite_test1", default_flavor=None, default_isolation="vm")
        image = MockImage(name="trusty-server-multi-nic")
        deployment = MockDeployment(name="testdeployment")
        owner.slices.count.return_value = 1
        owner.slices.all.return_value = [slice]
        owner.slices.first.return_value = slice
        get_image.return_value = image
        pick.return_value = (node, None)
        site_deployment.deployment = deployment
        flavor_objects.filter.return_value = []
        # done setup mocks

        with self.assertRaises(Exception) as e:
            self.policy.manage_container(self.tenant)
        self.assertEqual(e.exception.message, "No m1.small flavor")

if __name__ == '__main__':
    unittest.main()
