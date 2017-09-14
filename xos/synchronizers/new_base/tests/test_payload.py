
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
from multistructlog import create_logger

log = create_logger()

ANSIBLE_FILE='/tmp/payload_test'

def run_fake_ansible_template(*args,**kwargs):
    opts = args[1]
    open(ANSIBLE_FILE,'w').write(json.dumps(opts))

def get_ansible_output():
    ansible_str = open(ANSIBLE_FILE).read()
    return json.loads(ansible_str)

class TestPayload(unittest.TestCase):
    def setUp(self):
        b = backend.Backend()
        steps_dir = Config.get("steps_dir")
        self.steps = b.load_sync_step_modules(steps_dir)
        self.synchronizer = event_loop.XOSObserver(self.steps)

    @mock.patch("steps.sync_instances.syncstep.run_template",side_effect=run_fake_ansible_template)
    @mock.patch("event_loop.model_accessor")
    def test_delete_record(self, mock_run_template, mock_modelaccessor):
        o = Instance()
        o.name = "Sisi Pascal"

        o.synchronizer_step = steps.sync_instances.SyncInstances()
        self.synchronizer.delete_record(o, log)

        a = get_ansible_output()
        self.assertDictContainsSubset({'delete':True, 'name':o.name}, a)
        o.save.assert_called_with(update_fields=['backend_need_reap'])
        
    @mock.patch("steps.sync_instances.syncstep.run_template",side_effect=run_fake_ansible_template)
    @mock.patch("event_loop.model_accessor")
    def test_sync_record(self, mock_run_template, mock_modelaccessor):
        o = Instance()
        o.name = "Sisi Pascal"

        o.synchronizer_step = steps.sync_instances.SyncInstances()
        self.synchronizer.sync_record(o, log)

        a = get_ansible_output()
        self.assertDictContainsSubset({'delete':False, 'name':o.name}, a)
        o.save.assert_called_with(update_fields=['enacted', 'backend_status', 'backend_register'])

    @mock.patch("steps.sync_instances.syncstep.run_template",side_effect=run_fake_ansible_template)
    @mock.patch("event_loop.model_accessor")
    def test_sync_cohort(self, mock_run_template, mock_modelaccessor):
        cs = ControllerSlice()
        s = Slice(name = 'SP SP')
        cs.slice = s

        o = Instance()
        o.name = "Sisi Pascal"
        o.slice = s

        cohort = [cs, o]
        o.synchronizer_step = steps.sync_instances.SyncInstances()
        cs.synchronizer_step = steps.sync_controller_slices.SyncControllerSlices()

        self.synchronizer.sync_cohort(cohort, False)

        a = get_ansible_output()
        self.assertDictContainsSubset({'delete':False, 'name':o.name}, a)
        o.save.assert_called_with(update_fields=['enacted', 'backend_status', 'backend_register'])
        cs.save.assert_called_with(update_fields=['enacted', 'backend_status', 'backend_register'])

    @mock.patch("steps.sync_instances.syncstep.run_template",side_effect=run_fake_ansible_template)
    @mock.patch("event_loop.model_accessor")
    def test_deferred_exception(self, mock_run_template, mock_modelaccessor):
        cs = ControllerSlice()
        s = Slice(name = 'SP SP')
        cs.slice = s
        cs.force_defer = True

        o = Instance()
        o.name = "Sisi Pascal"
        o.slice = s

        cohort = [cs, o]
        o.synchronizer_step = steps.sync_instances.SyncInstances()
        cs.synchronizer_step = steps.sync_controller_slices.SyncControllerSlices()

        self.synchronizer.sync_cohort(cohort, False)
        o.save.assert_called_with(always_update_timestamp=True, update_fields=['backend_status', 'backend_register'])
        self.assertEqual(cs.backend_code, 1)

        self.assertIn('Force', cs.backend_status)
        self.assertIn('Failed due to', o.backend_status)

    @mock.patch("steps.sync_instances.syncstep.run_template",side_effect=run_fake_ansible_template)
    @mock.patch("event_loop.model_accessor")
    def test_backend_status(self, mock_run_template, mock_modelaccessor):
        cs = ControllerSlice()
        s = Slice(name = 'SP SP')
        cs.slice = s
        cs.force_fail = True

        o = Instance()
        o.name = "Sisi Pascal"
        o.slice = s

        cohort = [cs, o]
        o.synchronizer_step = steps.sync_instances.SyncInstances()
        cs.synchronizer_step = steps.sync_controller_slices.SyncControllerSlices()

        self.synchronizer.sync_cohort(cohort, False)
        o.save.assert_called_with(always_update_timestamp=True, update_fields=['backend_status', 'backend_register'])
        self.assertIn('Force', cs.backend_status)
        self.assertIn('Failed due to', o.backend_status)

    @mock.patch("steps.sync_instances.syncstep.run_template",side_effect=run_fake_ansible_template)
    @mock.patch("event_loop.model_accessor")
    def test_fetch_pending(self, mock_run_template, mock_accessor, *_other_accessors):
        pending_objects, pending_steps = self.synchronizer.fetch_pending()
        pending_objects2 = list(pending_objects)

        any_cs = next(obj for obj in pending_objects if obj.leaf_model_name == 'ControllerSlice')
        any_instance = next(obj for obj in pending_objects2 if obj.leaf_model_name == 'Instance')

        slice = Slice()
        any_instance.slice = slice
        any_cs.slice = slice

        self.synchronizer.external_dependencies = []
        cohorts = self.synchronizer.compute_dependent_cohorts(pending_objects, False)
        flat_objects = [item for cohort in cohorts for item in cohort]
       
        self.assertEqual(set(flat_objects), set(pending_objects))
    
    @mock.patch("steps.sync_instances.syncstep.run_template",side_effect=run_fake_ansible_template)
    @mock.patch("event_loop.model_accessor")
    def test_fetch_pending_with_external_dependencies(self, mock_run_template, mock_accessor, *_other_accessors):
        pending_objects, pending_steps = self.synchronizer.fetch_pending()
        pending_objects2 = list(pending_objects)

        self.synchronizer = event_loop.XOSObserver(self.steps)

        any_cn = next(obj for obj in pending_objects if obj.leaf_model_name == 'ControllerNetwork')
        any_user = next(obj for obj in pending_objects2 if obj.leaf_model_name == 'User')

        cohorts = self.synchronizer.compute_dependent_cohorts(pending_objects, False)
       
        flat_objects = [item for cohort in cohorts for item in cohort]
        self.assertEqual(set(flat_objects), set(pending_objects))

        # These cannot be None, but for documentation purposes
        self.assertIsNotNone(any_cn)
        self.assertIsNotNone(any_user)

    @mock.patch("steps.sync_instances.syncstep.run_template",side_effect=run_fake_ansible_template)
    @mock.patch("event_loop.model_accessor")
    def test_external_dependency_exception(self, mock_run_template, mock_modelaccessor):
        cs = ControllerSlice()
        s = Slice(name = 'SP SP')
        cs.slice = s

        o = Instance()
        o.name = "Sisi Pascal"
        o.slice = s

        cohort = [cs, o]
        o.synchronizer_step = None
        o.synchronizer_step = steps.sync_instances.SyncInstances()

        self.synchronizer.sync_cohort(cohort, False)

if __name__ == '__main__':
    unittest.main()
