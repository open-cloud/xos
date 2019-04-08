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
import os
from xosgenx.validator import XProtoValidator
from xosgenx.generator import XOSProcessor, XOSProcessorArgs
from mock import patch
import yaml

# Generate other formats from xproto


class XProtoValidatorTest(unittest.TestCase):
    def test_suggested_max_length(self):
        args = XOSProcessorArgs()
        args.files = ["/tmp/testvalidator.xproto"]

        open("/tmp/testvalidator.xproto", "w").write("""
            option app_label = "test";

            message Port (XOSBase){
                required string foo = 1 [max_length=254];
            }
            """)
        args.target = "modeldefs.xtarget"

        with patch.object(XProtoValidator, "print_errors", autospec=True) as print_errors:
            print_errors.return_value = None

            output = XOSProcessor.process(args)

            self.assertEqual(print_errors.call_count, 1)
            validator = print_errors.call_args[0][0]

            self.assertEqual(len(validator.errors), 1)
            self.assertEqual(validator.errors[0]["severity"], "WARNING")
            self.assertEqual(validator.errors[0]["message"], "max_length of 254 is close to suggested max_length of 256")

    def test_max_length_okay(self):
        args = XOSProcessorArgs()
        args.files = ["/tmp/testvalidator.xproto"]

        open("/tmp/testvalidator.xproto", "w").write("""
            option app_label = "test";

            message Port (XOSBase){
                required string foo = 1 [max_length=256];
            }
            """)
        args.target = "modeldefs.xtarget"

        with patch.object(XProtoValidator, "print_errors", autospec=True) as print_errors:
            print_errors.return_value = None

            output = XOSProcessor.process(args)

            self.assertEqual(print_errors.call_count, 0)

    def test_max_length_zero(self):
        args = XOSProcessorArgs()
        args.files = ["/tmp/testvalidator.xproto"]

        open("/tmp/testvalidator.xproto", "w").write("""
            option app_label = "test";

            message Port (XOSBase){
                required string foo = 1 [max_length=0];
            }
            """)
        args.target = "modeldefs.xtarget"

        with patch.object(XProtoValidator, "print_errors", autospec=True) as print_errors:
            print_errors.return_value = None

            output = XOSProcessor.process(args)

            self.assertEqual(print_errors.call_count, 1)
            validator = print_errors.call_args[0][0]

            self.assertEqual(len(validator.errors), 1)
            self.assertEqual(validator.errors[0]["severity"], "ERROR")
            self.assertEqual(validator.errors[0]["message"], "max_length should not be zero")


    def test_charfield_missing_max_length(self):
        args = XOSProcessorArgs()
        args.files = ["/tmp/testvalidator.xproto"]

        open("/tmp/testvalidator.xproto", "w").write("""
            option app_label = "test";

            message Port (XOSBase){
                required string foo = 1 [];
            }
            """)
        args.target = "modeldefs.xtarget"

        with patch.object(XProtoValidator, "print_errors", autospec=True) as print_errors:
            print_errors.return_value = None

            output = XOSProcessor.process(args)

            self.assertEqual(print_errors.call_count, 1)
            validator = print_errors.call_args[0][0]

            self.assertEqual(len(validator.errors), 1)
            self.assertEqual(validator.errors[0]["severity"], "ERROR")
            self.assertEqual(validator.errors[0]["message"], "String field should have a max_length or text=True")

if __name__ == "__main__":
    unittest.main()
