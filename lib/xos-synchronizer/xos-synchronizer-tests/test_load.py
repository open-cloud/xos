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

from __future__ import absolute_import
import unittest
from mock import patch
import mock
import pdb
import networkx as nx

import os
import sys

try:
    # Python 2: "reload" is built-in
    reload  # pylint: disable=reload-builtin
except NameError:
    from importlib import reload

test_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
sync_lib_dir = os.path.join(test_path, "..", "xossynchronizer")
xos_dir = os.path.join(test_path, "..", "..", "..", "xos")

class TestScheduling(unittest.TestCase):
    def setUp(self):
        self.sys_path_save = sys.path
        self.cwd_save = os.getcwd()

        config = os.path.join(test_path, "test_config.yaml")
        from xosconfig import Config

        Config.clear()
        Config.init(config, "synchronizer-config-schema.yaml")

        from xossynchronizer.mock_modelaccessor_build import (
            build_mock_modelaccessor,
        )

        build_mock_modelaccessor(sync_lib_dir, xos_dir, services_dir=None, service_xprotos=[])

        # The test config.yaml references files in `xos-synchronizer-tests/` so make sure we're in the parent
        # directory of the test directory.
        os.chdir(os.path.join(test_path, ".."))

        import xossynchronizer.event_loop
        reload(xossynchronizer.event_loop)

        import xossynchronizer.backend
        reload(xossynchronizer.backend)

        from xossynchronizer.modelaccessor import model_accessor

        b = xossynchronizer.backend.Backend(model_accessor=model_accessor)
        steps_dir = Config.get("steps_dir")
        self.steps = b.load_sync_step_modules(steps_dir)
        self.synchronizer = xossynchronizer.event_loop.XOSObserver(self.steps, model_accessor)

    def tearDown(self):
        sys.path = self.sys_path_save
        os.chdir(self.cwd_save)

    def test_load_steps(self):
        step_names = [s.__name__ for s in self.steps]
        self.assertIn("SyncPort", step_names)

    def test_load_deps(self):
        self.synchronizer.load_dependency_graph()
        graph = self.synchronizer.model_dependency_graph
        self.assertTrue(graph[False].has_edge("Slice", "Site"))
        self.assertTrue(graph[True].has_edge("Site", "Slice"))

    def test_load_sync_steps(self):
        self.synchronizer.load_sync_steps()
        model_to_step = self.synchronizer.model_to_step
        step_lookup = self.synchronizer.step_lookup
        self.assertIn(("Port", ["SyncPort"]), list(model_to_step.items()))
        self.assertIn(("Image", ["SyncImages"]), list(model_to_step.items()))

        for k, v in model_to_step.items():
            val = v[0]
            observes = step_lookup[val].observes
            if not isinstance(observes, list):
                observes = [observes]

            observed_names = []
            for o in observes:
                if isinstance(o,str):
                    observed_names.append(o)
                else:
                    observed_names.append(o.__name__)

            self.assertIn(k, observed_names)


if __name__ == "__main__":
    unittest.main()
