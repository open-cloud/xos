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
from xosgenx.generator import XOSProcessor
from helpers import FakeArgs, XProtoTestHelpers


class XProtoToscaTypeTest(unittest.TestCase):

    def setUp(self):
        self.target_tosca_type = XProtoTestHelpers.write_tmp_target(
            """
            {%- for m in proto.messages %}
            {% for f in m.fields %}
                {{ xproto_tosca_field_type(f.type) }}
            {% endfor -%}
            {% endfor -%}
            """)
    def test_tosca_fields(self):
        """
        [XOS-GenX] should convert xproto types to tosca know types
        """
        xproto = \
        """
        option app_label = "test";

        message Foo {
            required string name = 1 [ null = "False", blank="False"];
            required bool active = 1 [ null = "False", blank="False"];
            required int32 quantity = 1 [ null = "False", blank="False"];
        }
        """

        args = FakeArgs()
        args.inputs = xproto
        args.target = self.target_tosca_type
        output = XOSProcessor.process(args)
        self.assertIn('string', output)
        self.assertIn('boolean', output)
        self.assertIn('integer', output)

class XProtoToscaKeyTest(unittest.TestCase):

    def setUp(self):
        self.target_tosca_keys = XProtoTestHelpers.write_tmp_target(
            """
            {%- for m in proto.messages %}
                {{ xproto_fields_to_tosca_keys(m.fields) }}
            {% endfor -%}
            """)

    def test_xproto_fields_to_tosca_keys_default(self):
        """
        [XOS-GenX] if no "tosca_key" is specified, and a name attribute is present in the model, use that
        """
        xproto = \
"""
option app_label = "test";

message Foo {
    required string name = 1 [ null = "False", blank="False"];
}
"""

        args = FakeArgs()
        args.inputs = xproto
        args.target = self.target_tosca_keys
        output = XOSProcessor.process(args)
        self.assertIn('name', output)

    def test_xproto_fields_to_tosca_keys_custom(self):
        """
        [XOS-GenX] if "tosca_key" is specified, use it
        """
        xproto = \
            """
            option app_label = "test";
        
            message Foo {
                required string name = 1 [ null = "False", blank="False"];
                required string key_1 = 2 [ null = "False", blank="False", tosca_key=True];
                required string key_2 = 3 [ null = "False", blank="False", tosca_key=True];
            }
            """

        args = FakeArgs()
        args.inputs = xproto
        args.target = self.target_tosca_keys
        output = XOSProcessor.process(args)
        self.assertNotIn('name', output)
        self.assertIn('key_1', output)
        self.assertIn('key_2', output)

    def test_xproto_fields_link_to_tosca_keys_custom(self):
        """
        [XOS-GenX] if "tosca_key" is specified, use it
        """
        xproto = \
            """
            option app_label = "test";

            message Foo {
                required string name = 1 [ null = "False", blank="False"];
                required manytoone provider_service_instance->ServiceInstance:provided_links = 1 [db_index = True, null = False, blank = False, tosca_key=True];
            }
            """

        args = FakeArgs()
        args.inputs = xproto
        args.target = self.target_tosca_keys
        output = XOSProcessor.process(args)
        self.assertNotIn('name', output)
        self.assertIn('provider_service_instance_id', output)

    def test_xproto_model_to_oneof_key(self):
        """
        [XOS-GenX] in some models we need to have a combine key on variable fields, for example, keys can be subscriber_service_id + oneof(provider_service_id, provider_network_id)
        """
        xproto = \
            """
            option app_label = "test";

            message Foo {
            
                option tosca_key = "key1, oneof(key_2, key_3)";
            
                required string name = 1 [ null = "False", blank="False"];
                required string key_1 = 2 [ null = "False", blank="False", tosca_key_one_of = "key_2"];
                required string key_2 = 3 [ null = "False", blank="False", tosca_key_one_of = "key_1"];
                required string key_3 = 4 [ null = "False", blank="False", tosca_key_one_of = "key_4"];
                required string key_4 = 5 [ null = "False", blank="False", tosca_key_one_of = "key_3"];
            }
            """

        args = FakeArgs()
        args.inputs = xproto
        args.target = self.target_tosca_keys
        output = XOSProcessor.process(args)
        self.assertIn("['name', ['key_4', 'key_3'], ['key_1', 'key_2']]", output)

        xproto = \
            """
            option app_label = "test";

            message Foo {

                option tosca_key = "key1, oneof(key_2, key_3)";

                required string name = 1 [ null = "False", blank="False"];
                required manytoone key_1->Bar:key_1s = 2;
                required manytoone key_2->Bar:key_2s = 3 [tosca_key_one_of = "key_1"];
                required manytoone key_3->Bar:key_3s = 4 [tosca_key_one_of = "key_1"];
            }
            """

        args.inputs = xproto
        output = XOSProcessor.process(args)
        self.assertIn("['name', ['key_1_id', 'key_3_id', 'key_2_id']]", output)
