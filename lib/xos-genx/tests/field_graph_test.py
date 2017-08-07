
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
from xosgenx.jinja2_extensions import FieldNotFound
from helpers import FakeArgs, OUTPUT_DIR, XProtoTestHelpers
from xosgenx.generator import XOSGenerator

class XProtoFieldGraphTest(unittest.TestCase):
    def test_field_graph(self):
        xproto = \
"""
message VRouterDevice (PlCoreBase){
     optional string name = 1 [help_text = "device friendly name", max_length = 20, null = True, db_index = False, blank = True, unique_with="openflow_id"];
     required string openflow_id = 2 [help_text = "device identifier in ONOS", max_length = 20, null = False, db_index = False, blank = False, unique_with="name"];
     required string config_key = 3 [default = "basic", max_length = 32, blank = False, help_text = "configuration key", null = False, db_index = False, unique_with="driver"];
     required string driver = 4 [help_text = "driver type", max_length = 32, null = False, db_index = False, blank = False, unique_with="vrouter_service"];
     required manytoone vrouter_service->VRouterService:devices = 5 [db_index = True, null = False, blank = False];
     required string A = 6 [unique_with="B"];
     required string B = 7 [unique_with="C"];
     required string C = 8 [unique_with="A"];
     required string D = 9;
     required string E = 10 [unique_with="F,G"];
     required string F = 11;
     required string G = 12;
}
"""
	target = XProtoTestHelpers.write_tmp_target(
"""
{{ xproto_field_graph_components(proto.messages.0.fields) }}
""")

        args = FakeArgs()
        args.inputs = xproto
        args.target = target
        output = XOSGenerator.generate(args)
        output =  eval(output)
        self.assertIn({'A','B','C'}, output)
        self.assertIn({'openflow_id','name'}, output)
        self.assertIn({'config_key','vrouter_service','driver'}, output)
        self.assertIn({'E','F','G'}, output)
        
        union = reduce(lambda acc,x: acc | x, output)
        self.assertNotIn('D', union) 

    def test_missing_field(self):
        xproto = \
"""
message VRouterDevice (PlCoreBase){
     optional string name = 1 [help_text = "device friendly name", max_length = 20, null = True, db_index = False, blank = True, unique_with="hamburger"];
     required string openflow_id = 2 [help_text = "device identifier in ONOS", max_length = 20, null = False, db_index = False, blank = False, unique_with="name"];
     required string config_key = 3 [default = "basic", max_length = 32, blank = False, help_text = "configuration key", null = False, db_index = False, unique_with="driver"];
     required string driver = 4 [help_text = "driver type", max_length = 32, null = False, db_index = False, blank = False, unique_with="vrouter_service"];
     required manytoone vrouter_service->VRouterService:devices = 5 [db_index = True, null = False, blank = False];
     required string A = 6 [unique_with="B"];
     required string B = 7 [unique_with="C"];
     required string C = 8 [unique_with="A"];
     required string D = 9;
}
"""
	target = XProtoTestHelpers.write_tmp_target(
"""
{{ xproto_field_graph_components(proto.messages.0.fields) }}
""")

        def generate():
            args = FakeArgs()
            args.inputs = xproto
            args.target = target
            output = XOSGenerator.generate(args)

        # The following call generates some output, which should disappear
        # when Matteo merges his refactoring of XOSGenerator.
        self.assertRaises(FieldNotFound, generate)

if __name__ == '__main__':
    unittest.main()


