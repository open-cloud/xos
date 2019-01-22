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

import os
import sys
from xosconfig import Config

test_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
xos_dir = os.path.join(test_path, "..", "..", "..")


class TestModelPolicyTenantWithContainer(unittest.TestCase):
    def setUp(self):
        global TenantWithContainerPolicy, LeastLoadedNodeScheduler, MockObjectList

        self.sys_path_save = sys.path
        self.cwd_save = os.getcwd()
        sys.path.append(xos_dir)
        sys.path.append(os.path.join(xos_dir, "synchronizers", "new_base"))
        sys.path.append(
            os.path.join(xos_dir, "synchronizers", "new_base", "model_policies")
        )

        config = basic_conf = os.path.abspath(
            os.path.dirname(os.path.realpath(__file__)) + "/test_config.yaml"
        )
        Config.clear()  # in case left unclean by a previous test case
        Config.init(config, "synchronizer-config-schema.yaml")

        from synchronizers.new_base.mock_modelaccessor_build import (
            build_mock_modelaccessor,
        )

        build_mock_modelaccessor(xos_dir, services_dir=None, service_xprotos=[])

        import model_policy_tenantwithcontainer
        from model_policy_tenantwithcontainer import (
            TenantWithContainerPolicy,
            LeastLoadedNodeScheduler,
        )

        from mock_modelaccessor import MockObjectList

        # import all class names to globals
        for (
            k,
            v,
        ) in model_policy_tenantwithcontainer.model_accessor.all_model_classes.items():
            globals()[k] = v

        # TODO: Mock_model_accessor lacks save or delete methods
        # Instance.save = mock.Mock
        # Instance.delete = mock.Mock
        # TenantWithContainer.save = mock.Mock

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
        with patch.object(TenantWithContainer, "owner") as owner, patch.object(
            TenantWithContainer, "save"
        ) as tenant_save, patch.object(
            Node, "site_deployment"
        ) as site_deployment, patch.object(
            Instance, "save"
        ) as instance_save, patch.object(
            Instance, "delete"
        ) as instance_delete, patch.object(
            TenantWithContainerPolicy, "get_image"
        ) as get_image, patch.object(
            LeastLoadedNodeScheduler, "pick"
        ) as pick:
            # setup mocks
            node = Node(hostname="my.node.com")
            slice = Slice(
                name="mysite_test1", default_flavor=self.flavor, default_isolation="vm"
            )
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
        with patch.object(TenantWithContainer, "owner") as owner, patch.object(
            Node, "site_deployment"
        ) as site_deployment, patch.object(
            Flavor, "objects"
        ) as flavor_objects, patch.object(
            TenantWithContainerPolicy, "get_image"
        ) as get_image, patch.object(
            LeastLoadedNodeScheduler, "pick"
        ) as pick:
            # setup mocks
            node = Node(hostname="my.node.com")
            slice = Slice(
                name="mysite_test1", default_flavor=None, default_isolation="vm"
            )
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

    def test_least_loaded_node_scheduler(self):
        with patch.object(Node.objects, "get_items") as node_objects:
            slice = Slice(
                name="mysite_test1", default_flavor=None, default_isolation="vm"
            )
            node = Node(hostname="my.node.com", id=4567)
            node.instances = MockObjectList(initial=[])
            node_objects.return_value = [node]

            sched = LeastLoadedNodeScheduler(slice)
            (picked_node, parent) = sched.pick()

            self.assertNotEqual(picked_node, None)
            self.assertEqual(picked_node.id, node.id)

    def test_least_loaded_node_scheduler_two_nodes(self):
        with patch.object(Node.objects, "get_items") as node_objects:
            slice = Slice(
                name="mysite_test1", default_flavor=None, default_isolation="vm"
            )
            instance1 = Instance(id=1)
            node1 = Node(hostname="my.node.com", id=4567)
            node1.instances = MockObjectList(initial=[])
            node2 = Node(hostname="my.node.com", id=8910)
            node2.instances = MockObjectList(initial=[instance1])
            node_objects.return_value = [node1, node2]

            # should pick the node with the fewest instance (node1)

            sched = LeastLoadedNodeScheduler(slice)
            (picked_node, parent) = sched.pick()

            self.assertNotEqual(picked_node, None)
            self.assertEqual(picked_node.id, node1.id)

    def test_least_loaded_node_scheduler_two_nodes_multi(self):
        with patch.object(Node.objects, "get_items") as node_objects:
            slice = Slice(
                name="mysite_test1", default_flavor=None, default_isolation="vm"
            )
            instance1 = Instance(id=1)
            instance2 = Instance(id=2)
            instance3 = Instance(id=3)
            node1 = Node(hostname="my.node.com", id=4567)
            node1.instances = MockObjectList(initial=[instance2, instance3])
            node2 = Node(hostname="my.node.com", id=8910)
            node2.instances = MockObjectList(initial=[instance1])
            node_objects.return_value = [node1, node2]

            # should pick the node with the fewest instance (node2)

            sched = LeastLoadedNodeScheduler(slice)
            (picked_node, parent) = sched.pick()

            self.assertNotEqual(picked_node, None)
            self.assertEqual(picked_node.id, node2.id)

    def test_least_loaded_node_scheduler_with_label(self):
        with patch.object(Node.objects, "get_items") as node_objects:
            slice = Slice(
                name="mysite_test1", default_flavor=None, default_isolation="vm"
            )
            instance1 = Instance(id=1)
            node1 = Node(hostname="my.node.com", id=4567)
            node1.instances = MockObjectList(initial=[])
            node2 = Node(hostname="my.node.com", id=8910)
            node2.instances = MockObjectList(initial=[instance1])
            # Fake out the existence of a NodeLabel object. TODO: Extend the mock framework to support the model__field
            # syntax.
            node1.nodelabels__name = None
            node2.nodelabels__name = "foo"
            node_objects.return_value = [node1, node2]

            # should pick the node with the label, even if it has a greater number of instances

            sched = LeastLoadedNodeScheduler(slice, label="foo")
            (picked_node, parent) = sched.pick()

            self.assertNotEqual(picked_node, None)
            self.assertEqual(picked_node.id, node2.id)

    def test_least_loaded_node_scheduler_create_label(self):
        with patch.object(Node.objects, "get_items") as node_objects, patch.object(
            NodeLabel, "save", autospec=True
        ) as nodelabel_save, patch.object(NodeLabel, "node") as nodelabel_node_add:
            slice = Slice(
                name="mysite_test1", default_flavor=None, default_isolation="vm"
            )
            instance1 = Instance(id=1)
            node1 = Node(hostname="my.node.com", id=4567)
            node1.instances = MockObjectList(initial=[])
            node2 = Node(hostname="my.node.com", id=8910)
            node2.instances = MockObjectList(initial=[instance1])
            # Fake out the existence of a NodeLabel object. TODO: Extend the mock framework to support the model__field
            # syntax.
            node1.nodelabels__name = None
            node2.nodelabels__name = None
            node_objects.return_value = [node1, node2]

            # should pick the node with the least number of instances

            sched = LeastLoadedNodeScheduler(
                slice, label="foo", constrain_by_service_instance=True
            )
            (picked_node, parent) = sched.pick()

            self.assertNotEqual(picked_node, None)
            self.assertEqual(picked_node.id, node1.id)

            # NodeLabel should have been created and saved

            self.assertEqual(nodelabel_save.call_count, 1)
            self.assertEqual(nodelabel_save.call_args[0][0].name, "foo")

            # The NodeLabel's node field should have been added to

            NodeLabel.node.add.assert_called_with(node1)


if __name__ == "__main__":
    unittest.main()
