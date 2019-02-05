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
from mock import patch
import mock
import pdb
import networkx as nx

import os
import sys

test_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
sync_lib_dir = os.path.join(test_path, "..", "xossynchronizer")
xos_dir = os.path.join(test_path, "..", "..", "..", "xos")

ANSIBLE_FILE = "/tmp/payload_test"

log = None


def run_fake_ansible_template(*args, **kwargs):
    opts = args[1]
    open(ANSIBLE_FILE, "w").write(json.dumps(opts))
    return [{"rc": 0}]


def run_fake_ansible_template_fail(*args, **kwargs):
    opts = args[1]
    open(ANSIBLE_FILE, "w").write(json.dumps(opts))
    return [{"rc": 1}]


def get_ansible_output():
    ansible_str = open(ANSIBLE_FILE).read()
    return json.loads(ansible_str)


class TestPayload(unittest.TestCase):
    @classmethod
    def setUpClass(cls):

        global log

        config = os.path.join(test_path, "test_config.yaml")
        from xosconfig import Config

        Config.clear()
        Config.init(config, "synchronizer-config-schema.yaml")

        if not log:
            from multistructlog import create_logger

            log = create_logger(Config().get("logging"))

    def setUp(self):

        global log, test_steps, event_loop

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
        import test_steps.sync_instances
        import test_steps.sync_controller_slices
        from xossynchronizer.modelaccessor import model_accessor

        # import all class names to globals
        for (k, v) in model_accessor.all_model_classes.items():
            globals()[k] = v
        b = xossynchronizer.backend.Backend(model_accessor = model_accessor)
        steps_dir = Config.get("steps_dir")
        self.steps = b.load_sync_step_modules(steps_dir)
        self.synchronizer = xossynchronizer.event_loop.XOSObserver(self.steps, model_accessor)

    def tearDown(self):
        sys.path = self.sys_path_save
        os.chdir(self.cwd_save)

    @mock.patch(
        "test_steps.sync_instances.ansiblesyncstep.run_template",
        side_effect=run_fake_ansible_template,
    )
    def test_delete_record(self, mock_run_template):
        with mock.patch.object(Instance, "save") as instance_save:
            o = Instance()
            o.name = "Sisi Pascal"

            o.synchronizer_step = test_steps.sync_instances.SyncInstances(model_accessor = self.synchronizer.model_accessor)
            self.synchronizer.delete_record(o, log)

            a = get_ansible_output()
            self.assertDictContainsSubset({"delete": True, "name": o.name}, a)
            o.save.assert_called_with(update_fields=["backend_need_reap"])

    @mock.patch(
        "test_steps.sync_instances.ansiblesyncstep.run_template",
        side_effect=run_fake_ansible_template_fail,
    )
    def test_delete_record_fail(self, mock_run_template):
        with mock.patch.object(Instance, "save") as instance_save:
            o = Instance()
            o.name = "Sisi Pascal"

            o.synchronizer_step = test_steps.sync_instances.SyncInstances(model_accessor = self.synchronizer.model_accessor)

            with self.assertRaises(Exception) as e:
                self.synchronizer.delete_record(o, log)

            self.assertEqual(
                e.exception.message, "Nonzero rc from Ansible during delete_record"
            )

    @mock.patch(
        "test_steps.sync_instances.ansiblesyncstep.run_template",
        side_effect=run_fake_ansible_template,
    )
    def test_sync_record(self, mock_run_template):
        with mock.patch.object(Instance, "save") as instance_save:
            o = Instance()
            o.name = "Sisi Pascal"

            o.synchronizer_step = test_steps.sync_instances.SyncInstances(model_accessor = self.synchronizer.model_accessor)
            self.synchronizer.sync_record(o, log)

            a = get_ansible_output()
            self.assertDictContainsSubset({"delete": False, "name": o.name}, a)
            o.save.assert_called_with(
                update_fields=[
                    "enacted",
                    "backend_status",
                    "backend_register",
                    "backend_code",
                ]
            )

    @mock.patch(
        "test_steps.sync_instances.ansiblesyncstep.run_template",
        side_effect=run_fake_ansible_template,
    )
    def test_sync_cohort(self, mock_run_template):
        with mock.patch.object(Instance, "save") as instance_save, mock.patch.object(
            ControllerSlice, "save"
        ) as controllerslice_save:
            cs = ControllerSlice()
            s = Slice(name="SP SP")
            cs.slice = s

            o = Instance()
            o.name = "Sisi Pascal"
            o.slice = s

            cohort = [cs, o]
            o.synchronizer_step = test_steps.sync_instances.SyncInstances(model_accessor = self.synchronizer.model_accessor)
            cs.synchronizer_step = test_steps.sync_controller_slices.SyncControllerSlices(
                model_accessor = self.synchronizer.model_accessor
            )

            self.synchronizer.sync_cohort(cohort, False)

            a = get_ansible_output()
            self.assertDictContainsSubset({"delete": False, "name": o.name}, a)
            o.save.assert_called_with(
                update_fields=[
                    "enacted",
                    "backend_status",
                    "backend_register",
                    "backend_code",
                ]
            )
            cs.save.assert_called_with(
                update_fields=[
                    "enacted",
                    "backend_status",
                    "backend_register",
                    "backend_code",
                ]
            )

    @mock.patch(
        "test_steps.sync_instances.ansiblesyncstep.run_template",
        side_effect=run_fake_ansible_template,
    )
    def test_deferred_exception(self, mock_run_template):
        with mock.patch.object(Instance, "save") as instance_save:
            cs = ControllerSlice()
            s = Slice(name="SP SP")
            cs.slice = s
            cs.force_defer = True

            o = Instance()
            o.name = "Sisi Pascal"
            o.slice = s

            cohort = [cs, o]
            o.synchronizer_step = test_steps.sync_instances.SyncInstances(model_accessor=self.synchronizer.model_accessor)
            cs.synchronizer_step = test_steps.sync_controller_slices.SyncControllerSlices(
                model_accessor=self.synchronizer.model_accessor
            )

            self.synchronizer.sync_cohort(cohort, False)
            o.save.assert_called_with(
                always_update_timestamp=True,
                update_fields=["backend_status", "backend_register"],
            )
            self.assertEqual(cs.backend_code, 0)

            self.assertIn("Force", cs.backend_status)
            self.assertIn("Failed due to", o.backend_status)

    @mock.patch(
        "test_steps.sync_instances.ansiblesyncstep.run_template",
        side_effect=run_fake_ansible_template,
    )
    def test_backend_status(self, mock_run_template):
        with mock.patch.object(Instance, "save") as instance_save:
            cs = ControllerSlice()
            s = Slice(name="SP SP")
            cs.slice = s
            cs.force_fail = True

            o = Instance()
            o.name = "Sisi Pascal"
            o.slice = s

            cohort = [cs, o]
            o.synchronizer_step = test_steps.sync_instances.SyncInstances(model_accessor=self.synchronizer.model_accessor)
            cs.synchronizer_step = test_steps.sync_controller_slices.SyncControllerSlices(
                model_accessor=self.synchronizer.model_accessor)

            self.synchronizer.sync_cohort(cohort, False)
            o.save.assert_called_with(
                always_update_timestamp=True,
                update_fields=["backend_status", "backend_register"],
            )
            self.assertIn("Force", cs.backend_status)
            self.assertIn("Failed due to", o.backend_status)

    @mock.patch(
        "test_steps.sync_instances.ansiblesyncstep.run_template",
        side_effect=run_fake_ansible_template,
    )
    def test_fetch_pending(self, mock_run_template):
        pending_objects, pending_steps = self.synchronizer.fetch_pending()
        pending_objects2 = list(pending_objects)

        any_cs = next(
            obj for obj in pending_objects if obj.leaf_model_name == "ControllerSlice"
        )
        any_instance = next(
            obj for obj in pending_objects2 if obj.leaf_model_name == "Instance"
        )

        slice = Slice()
        any_instance.slice = slice
        any_cs.slice = slice

        self.synchronizer.external_dependencies = []
        cohorts = self.synchronizer.compute_dependent_cohorts(pending_objects, False)
        flat_objects = [item for cohort in cohorts for item in cohort]

        self.assertEqual(set(flat_objects), set(pending_objects))

    @mock.patch(
        "test_steps.sync_instances.ansiblesyncstep.run_template",
        side_effect=run_fake_ansible_template,
    )
    def test_fetch_pending_with_external_dependencies(
        self, mock_run_template,
    ):
        pending_objects, pending_steps = self.synchronizer.fetch_pending()
        pending_objects2 = list(pending_objects)

        any_cn = next(
            obj for obj in pending_objects if obj.leaf_model_name == "ControllerNetwork"
        )
        any_user = next(
            obj for obj in pending_objects2 if obj.leaf_model_name == "User"
        )

        cohorts = self.synchronizer.compute_dependent_cohorts(pending_objects, False)

        flat_objects = [item for cohort in cohorts for item in cohort]
        self.assertEqual(set(flat_objects), set(pending_objects))

        # These cannot be None, but for documentation purposes
        self.assertIsNotNone(any_cn)
        self.assertIsNotNone(any_user)

    @mock.patch(
        "test_steps.sync_instances.ansiblesyncstep.run_template",
        side_effect=run_fake_ansible_template,
    )
    def test_external_dependency_exception(self, mock_run_template):
        cs = ControllerSlice()
        s = Slice(name="SP SP")
        cs.slice = s

        o = Instance()
        o.name = "Sisi Pascal"
        o.slice = s

        cohort = [cs, o]
        o.synchronizer_step = None
        o.synchronizer_step = test_steps.sync_instances.SyncInstances(model_accessor=self.synchronizer.model_accessor)

        self.synchronizer.sync_cohort(cohort, False)


if __name__ == "__main__":
    unittest.main()
