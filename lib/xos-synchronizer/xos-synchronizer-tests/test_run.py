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

import json
import unittest
import mock

import os
import sys

test_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
sync_lib_dir = os.path.join(test_path, "..", "xossynchronizer")
xos_dir = os.path.join(test_path, "..", "..", "..", "xos")

ANSIBLE_FILE = "/tmp/payload_test"


def run_fake_ansible_template(*args, **kwargs):
    opts = args[1]
    open(ANSIBLE_FILE, "w").write(json.dumps(opts))


def get_ansible_output():
    ansible_str = open(ANSIBLE_FILE).read()
    return json.loads(ansible_str)


class TestRun(unittest.TestCase):
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

        os.chdir(os.path.join(test_path, ".."))  # config references xos-synchronizer-tests/model-deps

        import xossynchronizer.event_loop

        reload(xossynchronizer.event_loop)
        import xossynchronizer.backend

        reload(xossynchronizer.backend)
        from xossynchronizer.modelaccessor import model_accessor

        # import all class names to globals
        for (k, v) in model_accessor.all_model_classes.items():
            globals()[k] = v

        from xossynchronizer.modelaccessor import model_accessor

        b = xossynchronizer.backend.Backend(model_accessor=model_accessor)
        steps_dir = Config.get("steps_dir")
        self.steps = b.load_sync_step_modules(steps_dir)
        self.synchronizer = xossynchronizer.event_loop.XOSObserver(self.steps, model_accessor)
        try:
            os.remove("/tmp/sync_ports")
        except OSError:
            pass
        try:
            os.remove("/tmp/delete_ports")
        except OSError:
            pass

    def tearDown(self):
        sys.path = self.sys_path_save
        os.chdir(self.cwd_save)

    def test_run_once(self):
        pending_objects, pending_steps = self.synchronizer.fetch_pending()
        pending_objects2 = list(pending_objects)

        slice = Slice()

        self.synchronizer.run_once()

        sync_ports = open("/tmp/sync_ports").read()
        delete_ports = open("/tmp/delete_ports").read()

        self.assertIn("successful", sync_ports)
        self.assertIn("successful", delete_ports)


if __name__ == "__main__":
    unittest.main()
