
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

config =  os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + "/test_config_onos.yaml")
from xosconfig import Config
Config.init(config, 'synchronizer-config-schema.yaml')

import synchronizers.new_base.modelaccessor
from steps.mock_modelaccessor import *
import event_loop
import backend

class TestServices(unittest.TestCase):
    def setUp(self):
        b = backend.Backend()
        steps_dir = Config.get("steps_dir")
        self.steps = b.load_sync_step_modules(steps_dir)
        self.synchronizer = event_loop.XOSObserver(self.steps)

    def test_service_models(self):
        a = ONOSApp()
        s = ONOSService()

        cohorts = self.synchronizer.compute_dependent_cohorts([a,s], False)
        self.assertIn([s,a], cohorts)

        cohorts = self.synchronizer.compute_dependent_cohorts([s,a], False)
        self.assertIn([s,a], cohorts)

        cohorts = self.synchronizer.compute_dependent_cohorts([a,s], True)
        self.assertIn([a,s], cohorts)

        cohorts = self.synchronizer.compute_dependent_cohorts([s,a], True)
        self.assertIn([a,s], cohorts)

if __name__ == '__main__':
    unittest.main()
