
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
import mock
import event_loop
import backend
import json

import steps.sync_instances
import steps.sync_controller_slices

ANSIBLE_FILE='/tmp/payload_test'

def run_fake_ansible_template(*args,**kwargs):
    opts = args[1]
    open(ANSIBLE_FILE,'w').write(json.dumps(opts))

def get_ansible_output():
    ansible_str = open(ANSIBLE_FILE).read()
    return json.loads(ansible_str)

class TestRun(unittest.TestCase):
    def setUp(self):
        b = backend.Backend()
        steps_dir = Config.get("steps_dir")
        self.steps = b.load_sync_step_modules(steps_dir)
        self.synchronizer = event_loop.XOSObserver(self.steps)
        try:
            os.remove('/tmp/sync_ports')
        except OSError:
            pass
        try:
            os.remove('/tmp/delete_ports')
        except OSError:
            pass

    @mock.patch("steps.sync_instances.syncstep.run_template",side_effect=run_fake_ansible_template)
    @mock.patch("event_loop.model_accessor")
    def test_run_once(self, mock_run_template, mock_accessor, *_other_accessors):
        pending_objects, pending_steps = self.synchronizer.fetch_pending()
        pending_objects2 = list(pending_objects)

        any_cs = next(obj for obj in pending_objects if obj.leaf_model_name == 'ControllerSlice')
        any_instance = next(obj for obj in pending_objects2 if obj.leaf_model_name == 'Instance')

        slice = Slice()
        any_instance.slice = slice
        any_cs.slice = slice

        self.synchronizer.run_once()
        sync_ports = open('/tmp/sync_ports').read()
        delete_ports = open('/tmp/delete_ports').read()

        self.assertIn("successful", sync_ports)
        self.assertIn("successful", delete_ports)
    

if __name__ == '__main__':
    unittest.main()
