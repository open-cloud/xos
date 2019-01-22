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
from mock import patch, call, Mock, PropertyMock
import json

import os
import sys

# Hack to load synchronizer framework
test_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
xos_dir = os.path.join(test_path, "../../..")
if not os.path.exists(os.path.join(test_path, "new_base")):
    xos_dir = os.path.join(test_path, "../../../../../../orchestration/xos/xos")
    services_dir = os.path.join(xos_dir, "../../xos_services")
sys.path.append(xos_dir)
sys.path.append(os.path.join(xos_dir, "synchronizers", "new_base"))
# END Hack to load synchronizer framework


class TestDiffs(unittest.TestCase):

    """ These tests are for the mock modelaccessor, to make sure it behaves like the real one """

    def setUp(self):

        self.sys_path_save = sys.path
        sys.path.append(xos_dir)
        sys.path.append(os.path.join(xos_dir, "synchronizers", "new_base"))

        # Setting up the config module
        from xosconfig import Config

        config = os.path.join(test_path, "test_config.yaml")
        Config.clear()
        Config.init(config, "synchronizer-config-schema.yaml")
        # END Setting up the config module

        from synchronizers.new_base.mock_modelaccessor_build import (
            build_mock_modelaccessor,
        )

        # FIXME this is to get jenkins to pass the tests, somehow it is running tests in a different order
        # and apparently it is not overriding the generated model accessor
        build_mock_modelaccessor(xos_dir, services_dir, [])
        import synchronizers.new_base.modelaccessor

        # import all class names to globals
        for (
            k,
            v,
        ) in (
            synchronizers.new_base.modelaccessor.model_accessor.all_model_classes.items()
        ):
            globals()[k] = v

        self.log = Mock()

    def tearDown(self):
        sys.path = self.sys_path_save

    def test_new_diff(self):
        site = Site(name="mysite")

        self.assertEqual(site.is_new, True)
        self.assertEqual(site._dict, {"name": "mysite"})
        self.assertEqual(site.diff, {})
        self.assertEqual(site.changed_fields, ["name"])
        self.assertEqual(site.has_field_changed("name"), False)
        self.assertEqual(site.has_field_changed("login_base"), False)

        site.login_base = "bar"

        self.assertEqual(site._dict, {"login_base": "bar", "name": "mysite"})
        self.assertEqual(site.diff, {"login_base": (None, "bar")})
        self.assertIn("name", site.changed_fields)
        self.assertIn("login_base", site.changed_fields)
        self.assertEqual(site.has_field_changed("name"), False)
        self.assertEqual(site.has_field_changed("login_base"), True)
        self.assertEqual(site.get_field_diff("login_base"), (None, "bar"))

    def test_existing_diff(self):
        site = Site(name="mysite", login_base="foo")

        # this is what would happen after saving and re-loading
        site.is_new = False
        site.id = 1
        site._initial = site._dict

        self.assertEqual(site.is_new, False)
        self.assertEqual(site._dict, {"id": 1, "name": "mysite", "login_base": "foo"})
        self.assertEqual(site.diff, {})
        self.assertEqual(site.changed_fields, [])
        self.assertEqual(site.has_field_changed("name"), False)
        self.assertEqual(site.has_field_changed("login_base"), False)

        site.login_base = "bar"

        self.assertEqual(site._dict, {"id": 1, "login_base": "bar", "name": "mysite"})
        self.assertEqual(site.diff, {"login_base": ("foo", "bar")})
        self.assertIn("login_base", site.changed_fields)
        self.assertEqual(site.has_field_changed("name"), False)
        self.assertEqual(site.has_field_changed("login_base"), True)


if __name__ == "__main__":
    unittest.main()
