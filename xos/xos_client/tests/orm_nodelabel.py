
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

TEST_NODE_LABEL_1_NAME = "test_node_label_1"

class TestORM(unittest.TestCase):
    def setUp(self):
        self.test_node_label_1_name = TEST_NODE_LABEL_1_NAME + "_" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))

        nodes1 = orm.Node.objects.filter(name="test_node_1")
        if nodes1:
            self.node1=nodes1[0]
        else:
            self.node1 = orm.Node(name="test_node_1", site_deployment=orm.SiteDeployment.objects.first())
            self.node1.save()

        nodes2 = orm.Node.objects.filter(name="test_node_2")
        if nodes2:
            self.node2=nodes2[0]
        else:
            self.node2 = orm.Node(name="test_node_2", site_deployment=orm.SiteDeployment.objects.first())
            self.node2.save()

    def tearDown(self):
        # TODO: Deleting NodeLabel seems to be broken -- appears to be a cascade failure
        # attaching a nodelabel to a node causes deleting the node to also be broken.


        #node_labels1 = orm.NodeLabel.objects.filter(name=self.test_node_label_1_name)
        #for node_label in node_labels1:
        #    node_label.delete()

        #nodes1 = orm.Node.objects.filter(name="test_node_1")
        #for node in nodes1:
        #    node.delete()

        #nodes2 = orm.Node.objects.filter(name="test_node_2")
        #for node in nodes2:
        #    node.delete()

        pass

    def test_create_empty_node_label(self):
        n = orm.NodeLabel(name = self.test_node_label_1_name)
        n.save()

        labels = orm.NodeLabel.objects.filter(name = self.test_node_label_1_name)
        self.assertEqual(len(labels),1)

        n=labels[0]
        self.assertNotEqual(n, None)
        self.assertEqual(len(n.node.all()), 0)

    def test_create_node_label_one_node(self):
        n = orm.NodeLabel(name = self.test_node_label_1_name)
        n.node.add(self.node1)
        n.save()

        labels = orm.NodeLabel.objects.filter(name = self.test_node_label_1_name)
        self.assertEqual(len(labels),1)

        n=labels[0]
        self.assertNotEqual(n, None)
        self.assertEqual(len(n.node.all()), 1)

    def test_create_node_label_two_nodes(self):
        n = orm.NodeLabel(name = self.test_node_label_1_name)
        n.node.add(self.node1)
        n.node.add(self.node2)
        n.save()

        labels = orm.NodeLabel.objects.filter(name = self.test_node_label_1_name)
        self.assertEqual(len(labels),1)

        n=labels[0]
        self.assertNotEqual(n, None)
        self.assertEqual(len(n.node.all()), 2)

    def test_add_node_to_label(self):
        n = orm.NodeLabel(name = self.test_node_label_1_name)
        n.save()

        labels = orm.NodeLabel.objects.filter(name = self.test_node_label_1_name)
        self.assertEqual(len(labels), 1)
        n=labels[0]
        n.node.add(self.node1)
        n.save()

        labels = orm.NodeLabel.objects.filter(name = self.test_node_label_1_name)
        self.assertEqual(len(labels), 1)
        n=labels[0]
        self.assertEqual(len(n.node.all()), 1)

    def test_remove_node_from_label(self):
        n = orm.NodeLabel(name=self.test_node_label_1_name)
        n.node.add(self.node1)
        n.node.add(self.node2)
        n.save()

        labels = orm.NodeLabel.objects.filter(name=self.test_node_label_1_name)
        self.assertEqual(len(labels), 1)
        n = labels[0]
        self.assertEqual(len(n.node.all()), 2)
        n.node.remove(self.node1)
        n.save()

        labels = orm.NodeLabel.objects.filter(name=self.test_node_label_1_name)
        self.assertEqual(len(labels), 1)
        n = labels[0]
        self.assertEqual(len(n.node.all()), 1)

    def test_remove_last_node_from_label(self):
        n = orm.NodeLabel(name=self.test_node_label_1_name)
        n.node.add(self.node1)
        n.save()

        labels = orm.NodeLabel.objects.filter(name=self.test_node_label_1_name)
        self.assertEqual(len(labels), 1)
        n = labels[0]
        self.assertEqual(len(n.node.all()), 1)
        n.node.remove(self.node1)
        n.save(update_fields=["node_ids"])

        labels = orm.NodeLabel.objects.filter(name=self.test_node_label_1_name)
        self.assertEqual(len(labels), 1)
        n = labels[0]
        self.assertEqual(len(n.node.all()), 0)


def test_callback():
    global orm

    orm = xos_grpc_client.coreclient.xos_orm

    sys.argv=sys.argv[:1]  # unittest gets mad about the orm command line arguments
    unittest.main()

xos_grpc_client.start_api_parseargs(test_callback)

