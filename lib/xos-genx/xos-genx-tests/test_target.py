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
from helpers import XProtoTestHelpers, OUTPUT_DIR

TEST_FILE = "test_file"

TEST_OUTPUT = "Do re mi fa so la ti do"


class XProtoTargetTests(unittest.TestCase):
    def setUp(self):
        test_file = open(os.path.join(OUTPUT_DIR, TEST_FILE), "w")
        test_file.write(TEST_OUTPUT)
        test_file.close()

    def test_file_methods(self):
        target = XProtoTestHelpers.write_tmp_target(
            """
  {%% if file_exists("%s") %%}
    {{ include_file("%s") }}
  {%% endif %%}
"""
            % (TEST_FILE, TEST_FILE)
        )

        args = XOSProcessorArgs()
        args.inputs = ""
        args.target = target
        args.attic = OUTPUT_DIR
        output = XOSProcessor.process(args)
        self.assertIn(TEST_OUTPUT, output)

    def test_xproto_lib(self):
        target = XProtoTestHelpers.write_tmp_target(
            """
  {{ xproto_first_non_empty([None, None, None, None, None, None, "Eureka"]) }}
"""
        )
        args = XOSProcessorArgs()
        args.inputs = ""
        args.target = target
        output = XOSProcessor.process(args)
        self.assertIn("Eureka", output)

    def test_context(self):
        target = XProtoTestHelpers.write_tmp_target(
            """
  {{ context.what }}
"""
        )
        args = XOSProcessorArgs()
        args.inputs = ""
        args.target = target
        args.kv = "what:what is what"
        output = XOSProcessor.process(args)
        self.assertIn("what is what", output)

    def test_singularize(self):
        proto = """
  message TestSingularize {
      // The following field has an explicitly specified singular
      required int many = 1 [singular = "one"];
      // The following fields have automatically computed singulars
      required int sheep = 2;
      required int slices = 2;
      required int networks = 2;
      required int omf_friendlies = 2;
  }
"""

        target = XProtoTestHelpers.write_tmp_target(
            """
{% for m in proto.messages.0.fields -%}
{{ xproto_singularize(m) }},
{%- endfor %}
"""
        )
        args = XOSProcessorArgs()
        args.inputs = proto
        args.target = target
        output = XOSProcessor.process(args)
        self.assertEqual(
            "one,sheep,slice,network,omf_friendly", output.lstrip().rstrip().rstrip(",")
        )

    def test_pluralize(self):
        proto = """
  message TestPluralize {
      // The following field has an explicitly specified plural
      required int anecdote = 1 [plural = "data"];
      // The following fields have automatically computed plurals
      required int sheep = 2;
      required int slice = 2;
      required int network = 2;
      required int omf_friendly = 2;
  }
"""

        target = XProtoTestHelpers.write_tmp_target(
            """
{% for m in proto.messages.0.fields -%}
{{ xproto_pluralize(m) }},
{%- endfor %}
"""
        )
        args = XOSProcessorArgs()
        args.inputs = proto
        args.target = target
        output = XOSProcessor.process(args)
        self.assertEqual(
            "data,sheep,slices,networks,omf_friendlies",
            output.lstrip().rstrip().rstrip(","),
        )


if __name__ == "__main__":
    unittest.main()
