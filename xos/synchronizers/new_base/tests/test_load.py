
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
import networkx as nx

import os, sys

sys.path.append("../..")
sys.path.append("../../new_base")
config =  os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + "/test_config.yaml")
from xosconfig import Config
Config.init(config, 'synchronizer-config-schema.yaml')

import synchronizers.new_base.modelaccessor
from steps.mock_modelaccessor import *
import event_loop
import backend

class TestScheduling(unittest.TestCase):
    def setUp(self):
        # self.policy = TenantWithContainerPolicy()
        # self.user = User(email="testadmin@test.org")
        # self.tenant = Tenant(creator=self.user)
        # self.flavor = Flavor(name="m1.small")
        # model_policy_tenantwithcontainer.Instance = Instance
        # model_policy_tenantwithcontainer.Flavor = Flavor

        b = backend.Backend()
        steps_dir = Config.get("steps_dir")
        self.steps = b.load_sync_step_modules(steps_dir)
        self.synchronizer = event_loop.XOSObserver(self.steps)

    def test_load_steps(self):
        step_names = [s.__name__ for s in self.steps]
        self.assertIn('SyncControllerSlices', step_names)
    
    def test_load_deps(self):
        self.synchronizer.load_dependency_graph()
        graph = self.synchronizer.model_dependency_graph
        self.assertTrue(graph[False].has_edge('Instance','Slice'))
        self.assertTrue(graph[True].has_edge('Slice','Instance'))
        self.assertTrue(graph[False].has_edge('Slice','ControllerSlice'))
        self.assertTrue(graph[True].has_edge('ControllerSlice','Slice'))

    def test_load_dep_accessors(self):
        self.synchronizer.load_dependency_graph()
        graph = self.synchronizer.model_dependency_graph
        self.assertDictContainsSubset({'src_accessor': 'controllerslices'}, graph[False]['Slice']['ControllerSlice'])
        self.assertDictContainsSubset({'src_accessor': 'slice', 'dst_accessor': 'controllerslices'}, graph[True]['Slice']['ControllerSlice'])

    def test_load_sync_steps(self):
        self.synchronizer.load_sync_steps()
        model_to_step = self.synchronizer.model_to_step
        step_lookup = self.synchronizer.step_lookup
        self.assertIn(('ControllerSlice', ['SyncControllerSlices']), model_to_step.items())
        self.assertIn(('SiteRole', ['SyncRoles']), model_to_step.items())

        for k, v in model_to_step.items():
            val = v[0]
            observes = step_lookup[val].observes
            if not isinstance(observes, list):
                observes = [observes]

            observed_names = [o.__name__ for o in observes]
            self.assertIn(k, observed_names)

if __name__ == '__main__':
    unittest.main()
