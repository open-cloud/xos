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


class TestSyncTestserviceServiceInstance(unittest.TestCase):

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

        import xossynchronizer.modelaccessor
        import mock_modelaccessor
        imp.reload(mock_modelaccessor)  # in case nose2 loaded it in a previous test
        imp.reload(xossynchronizer.modelaccessor)  # in case nose2 loaded it in a previous test

        from sync_testservice_serviceinstance import SyncTestserviceServiceInstance
        from xossynchronizer.modelaccessor import model_accessor

        self.model_accessor = model_accessor

        # import all class names to globals
        for (k, v) in model_accessor.all_model_classes.items():
            globals()[k] = v

        self.sync_step = SyncTestserviceServiceInstance

        # TODO: Use modelaccessor instead
        # create a mock instance instance
        self.model = Mock(name="Example",
                          some_integer=0,
                          sync_after_policy=False,
                          sync_during_policy=False,
                          policy_after_sync=False,
                          policy_during_sync=False,
                          update_during_sync=False,
                          update_during_policy=False,
                          create_duplicate=False)

    def tearDown(self):
        self.model = None
        sys.path = self.sys_path_save

    # TODO - The following two tests are very simple, replace with more meaningful ones

    def test_save(self):
        # Tests that the model can be saved

        self.model.name = "testservice_test"
        self.model.update_during_sync = True
        self.sync_step(model_accessor=self.model_accessor).sync_record(self.model)
        self.model.save.assert_called()


if __name__ == '__main__':
    unittest.main()
