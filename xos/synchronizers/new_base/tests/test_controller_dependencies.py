
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

class TestControllerDependencies(unittest.TestCase):
    def setUp(self):
        b = backend.Backend()
        steps_dir = Config.get("steps_dir")
        self.steps = b.load_sync_step_modules(steps_dir)
        self.synchronizer = event_loop.XOSObserver(self.steps)

    def test_multi_controller_path(self):
        csl = ControllerSlice()
        csi = ControllerSite()
        site = Site()
        slice = Slice()
        slice.site = site
        csl.slice = slice
        csi.site = site
        slice.controllerslices = mock_enumerator([csl])
        site.controllersite = mock_enumerator([csi])

        verdict, edge_type = self.synchronizer.concrete_path_exists(csl, csi)
        self.assertTrue(verdict)
        self.assertEqual(edge_type, event_loop.PROXY_EDGE)

    def test_controller_path_simple(self):
        p = Instance()
        s = Slice()
        t = Site()
        ct = ControllerSite()
        p.slice = s
        s.site = t
        ct.site = t
        t.controllersite = mock_enumerator([ct])
        cohorts = self.synchronizer.compute_dependent_cohorts([p,ct], False)
        self.assertEqual([ct, p], cohorts[0])
        cohorts = self.synchronizer.compute_dependent_cohorts([ct,p], False)
        self.assertEqual([ct, p], cohorts[0])

    def test_controller_deletion_path(self):
        p = Instance()
        s = Slice()
        t = Site()
        ct = ControllerSite()
        ct.site = t
        p.slice = s
        s.site = t

        t.controllersite = mock_enumerator([ct])
        
        cohorts = self.synchronizer.compute_dependent_cohorts([p,s,t,ct], False)
        self.assertEqual([t, ct, s, p], cohorts[0])
        cohorts = self.synchronizer.compute_dependent_cohorts([p,s,t,ct], True)
        self.assertEqual([p, s, ct, t], cohorts[0])

    def test_multi_controller_schedule(self):
        csl = ControllerSlice()
        csi = ControllerSite()
        site = Site()
        slice = Slice()
        slice.site = site
        csl.slice = slice
        csi.site = site
        slice.controllerslices = mock_enumerator([csl])
        site.controllersite = mock_enumerator([csi])
        i = Instance()
        i.slice = slice

        cohorts = self.synchronizer.compute_dependent_cohorts([i, slice, site, csl, csi], False)
        self.assertEqual([site, csi, slice, csl, i], cohorts[0])

    def test_multi_controller_path_negative(self):
        csl = ControllerSlice()
        csi = ControllerSite()
        site = Site()
        slice = Slice()
        slice.site = site
        csl.slice = slice
        csi.site = site
        slice.controllerslices = mock_enumerator([])
        site.controllersite = mock_enumerator([])

        verdict, edge_type = self.synchronizer.concrete_path_exists(csl, csi)
        self.assertFalse(verdict)
        self.assertEqual(edge_type, None)

    def test_controller_path_simple_negative(self):
        p = Instance()
        s = Slice()
        t = Site()
        ct = ControllerSite()
        p.slice = s
        s.site = t
        ct.site = t
        t.controllersite = mock_enumerator([])
        cohorts = self.synchronizer.compute_dependent_cohorts([p,ct], False)
        self.assertIn([ct], cohorts)
        self.assertIn([p], cohorts)

    def test_controller_deletion_path_negative(self):
        p = Instance()
        s = Slice()
        t = Site()
        ct = ControllerSite()
        s.site = t

        t.controllersite = mock_enumerator([])
        
        cohorts = self.synchronizer.compute_dependent_cohorts([p,s,t,ct], False)
        self.assertIn([t,s], cohorts)
        self.assertIn([p], cohorts)
        self.assertIn([ct], cohorts)
        cohorts = self.synchronizer.compute_dependent_cohorts([p,s,t,ct], True)
        self.assertIn([s,t], cohorts)
        self.assertIn([p], cohorts)
        self.assertIn([ct], cohorts)


    def test_multi_controller_deletion_schedule(self):
        csl = ControllerSlice()
        cn = ControllerNetwork()
        site = Site()
        slice = Slice()
        slice.site = site
        slice.controllerslices = mock_enumerator([])
        site.controllersite = mock_enumerator([])
        i = Instance()
        i.slice = slice

        cohorts = self.synchronizer.compute_dependent_cohorts([i, slice, site, csl, csi], False)
        self.assertIn([site, slice, i], cohorts)
        self.assertIn([csl], cohorts)
        self.assertIn([csi], cohorts)

    def test_multi_controller_schedule_negative(self):
        csl = ControllerSlice()
        csi = ControllerSite()
        site = Site()
        slice = Slice()
        slice.site = site
        slice.controllerslices = mock_enumerator([])
        site.controllersite = mock_enumerator([])
        i = Instance()
        i.slice = slice

        cohorts = self.synchronizer.compute_dependent_cohorts([i, slice, site, csl, csi], False)
        self.assertIn([site, slice, i], cohorts)
        self.assertIn([csl], cohorts)
        self.assertIn([csi], cohorts)

if __name__ == '__main__':
    unittest.main()
