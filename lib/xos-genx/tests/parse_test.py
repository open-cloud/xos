
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
from xosgenx.generator import XOSGenerator
from helpers import FakeArgs, XProtoTestHelpers

class XProtoParseTests(unittest.TestCase):
    def test_global_options(self):

        xtarget = XProtoTestHelpers.write_tmp_target("{{ options }}")

        xproto = \
"""
    option kind = "vsg";
    option verbose_name = "vSG Service";
"""
        args = FakeArgs()
        args.inputs = xproto
        args.target = xtarget
        output = XOSGenerator.generate(args)
        self.assertIn("vsg", output)
        self.assertIn("vSG Service", output)

    def test_basic_proto(self):
        xtarget = XProtoTestHelpers.write_tmp_target("{{ proto }}")

        xproto = \
"""
message Person {
  required string name = 1;
  required int32 id = 2;  // Unique ID number for this person.
  optional string email = 3 [symphony = "da da da dum"];

  enum PhoneType {
    MOBILE = 0;
    HOME = 1;
    WORK = 2;
  }

  required  string number = 1;
  optional PhoneType type = 2;

  repeated PhoneNumber phones = 4;
}
"""
        args = FakeArgs()
        args.inputs = xproto
        args.target = xtarget
        output = XOSGenerator.generate(args)
        self.assertIn("PhoneNumber", output)

    def test_link_extensions(self):

        xtarget = XProtoTestHelpers.write_tmp_target("{{ proto.messages.0.links }}")
        xproto = \
"""
message links {
    required manytoone vrouter_service->VRouterService:device_ports = 4 [db_index = True, null = False, blank = False];
}
"""
        args = FakeArgs()
        args.inputs = xproto
        args.target = xtarget
        output = XOSGenerator.generate(args)
        self.assertIn("VRouterService", output)
	
	pass

    def test_through_extensions(self):
        xtarget = XProtoTestHelpers.write_tmp_target("{{ proto.messages.0.links.0.through }}")
        xproto = \
"""
message links {
    required manytomany vrouter_service->VRouterService/ServiceProxy:device_ports = 4 [db_index = True, null = False, blank = False];
}
"""
        args = FakeArgs()
        args.inputs = xproto
        args.target = xtarget
        output = XOSGenerator.generate(args)
        self.assertIn("ServiceProxy", output)

    def test_message_options(self):
        xtarget = XProtoTestHelpers.write_tmp_target("{{ proto.messages.0.options.type }}")
        xproto = \
"""
message link {
    option type = "e1000";
}
"""
        args = FakeArgs()
        args.inputs = xproto
        args.target = xtarget
        output = XOSGenerator.generate(args)
        self.assertIn("e1000", output)

	pass

    def test_message_base(self):
        xtarget = XProtoTestHelpers.write_tmp_target("{{ proto.messages.0.bases }}")
        xproto = \
"""
message base(Base) {
}
"""

        args = FakeArgs()
        args.inputs = xproto
        args.target = xtarget
        output = XOSGenerator.generate(args)
        self.assertIn("Base", output)

if __name__ == '__main__':
    unittest.main()


