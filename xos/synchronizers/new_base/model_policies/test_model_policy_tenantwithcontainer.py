
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
from xosconfig import Config

test_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
xos_dir = os.path.join(test_path, '..', '..', '..')

class TestModelPolicyTenantWithContainer(unittest.TestCase):
    def setUp(self):
        global TenantWithContainerPolicy, LeastLoadedNodeScheduler

        self.sys_path_save = sys.path
        self.cwd_save = os.getcwd()
        sys.path.append(xos_dir)
        #sys.path.append(os.path.join(xos_dir, 'synchronizers', 'new_base'))
        sys.path.append(os.path.join(xos_dir, 'synchronizers', 'new_base', 'model_policies'))

        config = basic_conf = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + "/test_config.yaml")
        Config.clear() # in case left unclean by a previous test case
        Config.init(config, 'synchronizer-config-schema.yaml')
        import model_policy_tenantwithcontainer
        from model_policy_tenantwithcontainer import TenantWithContainerPolicy, LeastLoadedNodeScheduler

        # import all class names to globals
        for (k, v) in model_policy_tenantwithcontainer.model_accessor.all_model_classes.items():
            globals()[k] = v

        # TODO: Mock_model_accessor lacks save or delete methods
        #Instance.save = mock.Mock
        #Instance.delete = mock.Mock
        #TenantWithContainer.save = mock.Mock

        self.policy = TenantWithContainerPolicy()
        self.user = User(email="testadmin@test.org")
        self.tenant = TenantWithContainer(creator=self.user)
        self.flavor = Flavor(name="m1.small")

    def tearDown(self):
        Config.clear()
        sys.path = self.sys_path_save
        os.chdir(self.cwd_save)

    def test_manage_container_no_slices(self):
        with patch.object(TenantWithContainer, "owner") as owner:
            owner.slices.count.return_value = 0
            with self.assertRaises(Exception) as e:
                self.policy.manage_container(self.tenant)
            self.assertEqual(e.exception.message, "The service has no slices")

    def test_manage_container(self):
      with patch.object(TenantWithContainer, "owner") as owner, \
           patch.object(TenantWithContainer, "save") as tenant_save, \
           patch.object(Node, "site_deployment") as site_deployment, \
           patch.object(Instance, "save") as instance_save, \
           patch.object(Instance, "delete") as instance_delete, \
           patch.object(TenantWithContainerPolicy, "get_image") as get_image, \
           patch.object(LeastLoadedNodeScheduler, "pick") as pick:
        # setup mocks
        node = Node(hostname="my.node.com")
        slice = Slice(name="mysite_test1", default_flavor=self.flavor, default_isolation="vm")
        image = Image(name="trusty-server-multi-nic")
        deployment = Deployment(name="testdeployment")
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

    def test_manage_container_no_m1_small(self):
      with patch.object(TenantWithContainer, "owner") as owner, \
           patch.object(Node, "site_deployment") as site_deployment, \
           patch.object(Flavor, "objects") as flavor_objects, \
           patch.object(TenantWithContainerPolicy, "get_image") as get_image, \
                patch.object(LeastLoadedNodeScheduler, "pick") as pick:
        # setup mocks
        node = Node(hostname="my.node.com")
        slice = Slice(name="mysite_test1", default_flavor=None, default_isolation="vm")
        image = Image(name="trusty-server-multi-nic")
        deployment = Deployment(name="testdeployment")
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
