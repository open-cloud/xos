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
from xosgenx.generator import XOSProcessor, XOSProcessorArgs
from helpers import OUTPUT_DIR

TEST_INPUT = """option name = "test_custom_python";
option app_label = "test_custom_python";

message ModelOne (XOSBase) {
    option custom_python = "True";
    optional manytoone model_two->ModelTwo:model_ones = 1:1001 [
        help_text = "FK from model_one to model_two",
        db_index = True];
}

message ModelTwo (XOSBase) {
    optional manytoone model_three->ModelThree:model_twos = 1:1001 [
        help_text = "FK from model_two to model_three",
        db_index = True];
}

message ModelThree (XOSBase) {
    option custom_python = "True";
}
"""


class XProtoCustomPythonTests(unittest.TestCase):
    def setUp(self):
        # Make sure the environment is clean before running tests
        self.cleanup()

    def tearDown(self):
        self.cleanup()

    def cleanup(self):
        for fn in [os.path.join(OUTPUT_DIR, "models_decl.py"),
                   os.path.join(OUTPUT_DIR, "modelthree_decl.py"),
                   os.path.join(OUTPUT_DIR, "modeltwo.py"),
                   os.path.join(OUTPUT_DIR, "modelone_decl.py")]:
            if os.path.exists(fn):
                os.remove(fn)

    def test_core(self):
        args = XOSProcessorArgs()
        args.inputs = TEST_INPUT
        args.write_to_file = "model"
        args.output = OUTPUT_DIR
        args.target = "django.xtarget"
        args.dest_extension = "py"
        XOSProcessor.process(args)

        modelone_decl_fn = os.path.join(OUTPUT_DIR, "modelone_decl.py")
        self.assertTrue(os.path.exists(modelone_decl_fn))
        m1output = open(modelone_decl_fn).read()

        modeltwo_fn = os.path.join(OUTPUT_DIR, "modeltwo.py")
        self.assertTrue(os.path.exists(modeltwo_fn))
        m2output = open(modeltwo_fn).read()

        modelthree_decl_fn = os.path.join(OUTPUT_DIR, "modelthree_decl.py")
        self.assertTrue(os.path.exists(modelthree_decl_fn))
        m3output = open(modelthree_decl_fn).read()

        # Every model should get a _decl
        self.assertIn("class ModelOne_decl(XOSBase):", m1output)
        self.assertIn("class ModelTwo_decl(XOSBase):", m2output)
        self.assertIn("class ModelThree_decl(XOSBase):", m3output)

        # ModelTwo has no custom_python so it should get a stub automatically
        self.assertIn("class ModelTwo(ModelTwo_decl):", m2output)

        # Foreign Keys always go to the derived models
        self.assertIn("model_two = ForeignKey(ModelTwo,", m1output)
        self.assertIn("model_three = ForeignKey(ModelThree,", m2output)

    def test_services(self):
        output_fn = os.path.join(OUTPUT_DIR, "models_decl.py")

        args = XOSProcessorArgs()
        args.inputs = TEST_INPUT
        args.write_to_file = "target"
        args.output = OUTPUT_DIR
        args.target = "service.xtarget"
        XOSProcessor.process(args)

        self.assertTrue(os.path.exists(output_fn))

        output = open(output_fn).read()

        # Every model should get a _decl
        self.assertIn("class ModelOne_decl(XOSBase):", output)
        self.assertIn("class ModelTwo_decl(XOSBase):", output)
        self.assertIn("class ModelThree_decl(XOSBase):", output)

        # ModelTwo has no custom_python so it should get a stub automatically
        self.assertIn("class ModelTwo(ModelTwo_decl):", output)

        # Foreign Keys always go to the decl models
        self.assertIn("model_two = ForeignKey(ModelTwo_decl,", output)
        self.assertIn("model_three = ForeignKey(ModelThree_decl,", output)


if __name__ == "__main__":
    unittest.main()
