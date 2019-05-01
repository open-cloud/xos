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
from xosgenx.generator import XOSProcessor, XOSProcessorArgs
from xosgenx.jinja2_extensions import xproto_validators
from helpers import XProtoTestHelpers


class XProtoGuiTest(unittest.TestCase):
    def setUp(self):
        self.target = XProtoTestHelpers.write_tmp_target(
            """
            {%- for m in proto.messages %}
            {% for f in m.fields %}
                {{ xproto_validators(f) }}
            {% endfor -%}
            {% endfor -%}
            """
        )

    def test_validators(self):
        field = {
            'modifier': 'required',
            'type': 'string',
            'options': {
                'max_length': '200',
                'modifier': 'required'
            }
        }

        res = xproto_validators(field)

        self.assertDictEqual(res[0], {'int_value': 200, 'name': 'maxlength'})
        self.assertDictEqual(res[1], {'bool_value': True, 'name': 'required'})

if __name__ == "__main__":
    unittest.main()