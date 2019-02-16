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

import os
import unittest

from xosutil import autodiscover_version

test_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))


class XOSUtilTest(unittest.TestCase):
    """
    Testing the XOS Util Module
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_autodiscover_version_of_caller(self):
        version = open(os.path.join(test_path, "../../../VERSION")).readline().strip()
        self.assertEqual(version, autodiscover_version.autodiscover_version_of_caller())

    def test_autodiscover_version_of_caller_save_to(self):
        version = open(os.path.join(test_path, "../../../VERSION")).readline().strip()
        test_save_fn = os.path.join(test_path, "test_version.py")
        if os.path.exists(test_save_fn):
            os.remove(test_save_fn)
        self.assertEqual(
            version,
            autodiscover_version.autodiscover_version_of_caller(
                save_to="test_version.py"
            ),
        )
        self.assertTrue(os.path.exists(test_save_fn))
        self.assertTrue(version in open(test_save_fn).read())


if __name__ == "__main__":
    unittest.main()
