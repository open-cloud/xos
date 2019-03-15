# Copyright 2018-present Open Networking Foundation
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

import imp
import os
import sys
import unittest
from mock import Mock

test_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))


class TestModelPolicyTestserviceServiceInstance(unittest.TestCase):

    def setUp(self):

        self.sys_path_save = sys.path

        # Setting up the config module
        from xosconfig import Config
        config = os.path.join(test_path, "../test_config.yaml")
        Config.clear()
        Config.init(config, "synchronizer-config-schema.yaml")
        # END Setting up the config module

        from xossynchronizer.mock_modelaccessor_build import build_mock_modelaccessor

        # Can't use mock_modelaccessor_config because we're not in the xos-services directory, so do it
        # the long way...
        xos_dir = os.path.join(test_path, "../../../../xos")
        services_dir = os.path.join(test_path, "../../../..")
        service_xprotos = [os.path.join(test_path, "../models/testservice.xproto")]
        build_mock_modelaccessor(None, xos_dir, services_dir, service_xprotos)
#        mock_modelaccessor_config(test_path, [("testservice", "testservice.xproto")])

        import xossynchronizer.modelaccessor
        import mock_modelaccessor
        imp.reload(mock_modelaccessor)  # in case nose2 loaded it in a previous test
        imp.reload(xossynchronizer.modelaccessor)  # in case nose2 loaded it in a previous test

        from model_policy_testservice_serviceinstance import TestserviceServiceInstancePolicy
        from xossynchronizer.modelaccessor import model_accessor

        self.model_accessor = model_accessor

        # import all class names to globals
        for (k, v) in model_accessor.all_model_classes.items():
            globals()[k] = v

        # Some of the functions we call have side-effects, reset the world.
        model_accessor.reset_all_object_stores()

        self.policy = TestserviceServiceInstancePolicy(self.model_accessor)
        self.si = Mock(sync_after_policy=False,
                       sync_during_policy=False,
                       policy_after_sync=False,
                       policy_during_sync=False,
                       update_during_sync=False,
                       update_during_policy=False,
                       create_duplicate=False)

    def tearDown(self):
        sys.path = self.sys_path_save
        self.si = None

#    def test_not_synced(self):
#        self.si.valid = "awaiting"
#        self.si.updated = 2
#        self.si.enacted = 1
#        self.si.backend_code = 0
#
#        with self.assertRaises(Exception) as e:
#            self.policy.handle_update(self.si)
#
#        self.assertIn("has not been synced yet", e.exception.message)

    def test_skip_update(self):
        self.si.valid = "awaiting"
        self.si.backend_code = 1

        self.policy.handle_update(self.si)


if __name__ == '__main__':
    unittest.main()
