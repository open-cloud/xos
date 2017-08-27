
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

    def test_concrete_path_no_model_path(self):
        p = Port()
        n = NetworkParameter()
        verdict = self.synchronizer.concrete_path_exists(p, n)
        self.assertFalse(verdict)

    def test_concrete_no_object_path_adjacent(self):
        p = Instance()
        s1 = Slice()
        s2 = Slice()
        p.slice = s2
        verdict = self.synchronizer.concrete_path_exists(p, s1)
        
        self.assertFalse(verdict)
    
    def test_concrete_object_path_adjacent(self):
        p = Instance()
        s = Slice()
        p.slice = s
        verdict = self.synchronizer.concrete_path_exists(p, s)
        
        self.assertTrue(verdict)

    def test_concrete_object_controller_path_adjacent(self):
        p = Instance()
        q = Instance()
        cs = ControllerSlice()
        cs2 = ControllerSlice()
        s1 = Slice()
        s2 = Slice()
        p.slice = s1
        q.slice = s2
        cs.slice = s1

        verdict1 = self.synchronizer.concrete_path_exists(p, cs)
        verdict2 = self.synchronizer.concrete_path_exists(q, cs)
        verdict3 = self.synchronizer.concrete_path_exists(p, cs2)
        
        self.assertTrue(verdict1)
        self.assertFalse(verdict2)
        self.assertFalse(verdict3)

    def test_concrete_object_controller_path_distant(self):
        p = Instance()
        s = Slice()
        t = Site()
        ct = ControllerSite()
        ct.site = t
        p.slice = s
        s.site = t
        verdict = self.synchronizer.concrete_path_exists(p, ct)
        self.assertTrue(verdict)

    def test_concrete_object_path_distant(self):
        p = Instance()
        s = Slice()
        t = Site()
        p.slice = s
        s.site = t
        verdict = self.synchronizer.concrete_path_exists(p, t)
        self.assertTrue(verdict)

    def test_concrete_no_object_path_distant(self):
        p = Instance()
        s = Slice()
        t = Site()
        ct = ControllerSite()
        ct.site = Site()
        p.slice = s
        s.site = t
        verdict = self.synchronizer.concrete_path_exists(p, ct)
        self.assertTrue(verdict)

    def test_cohorting_independent(self):
        i = Image()
        p = Slice()
        c = Instance()
        cohorts = self.synchronizer.compute_dependent_cohorts([i,p,c], False)
        self.assertEqual(len(cohorts), 3)
    
    def test_cohorting_related(self):
        i = Image()
        p = Port()
        c = Instance()
        c.image = i
        s = ControllerSlice()

        cohorts = self.synchronizer.compute_dependent_cohorts([i,p,c,s], False)
        self.assertIn([i,c], cohorts)
        self.assertIn([p], cohorts)
        self.assertIn([s], cohorts)

    def test_cohorting_related_multi(self):
        i = Image()
        p = Port()
        c = Instance()
        c.image = i
        cs = ControllerSlice()
        s = Slice()
        cs.slice = s
        c.slice = s

        cohorts = self.synchronizer.compute_dependent_cohorts([i,p,c,s,cs], False)

        big_cohort = max(cohorts, key=len)
        self.assertGreater(big_cohort.index(c), big_cohort.index(i))
        self.assertGreater(big_cohort.index(cs), big_cohort.index(s))
        self.assertIn([p], cohorts)

    def test_cohorting_related_delete(self):
        i = Image()
        p = Port()
        c = Instance()
        c.image = i
        s = ControllerSlice()

        cohorts = self.synchronizer.compute_dependent_cohorts([i,p,c,s], True)
        self.assertIn([c,i], cohorts)
        self.assertIn([p], cohorts)
        self.assertIn([s], cohorts)

if __name__ == '__main__':
    unittest.main()
