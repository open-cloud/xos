
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
import os
from xosgenx.generator import XOSGenerator
from helpers import FakeArgs

VROUTER_XPROTO = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + "/xproto/vrouterport.xproto")

# Generate Protobuf from Xproto and then parse the resulting Protobuf
class XProtoProtobufGeneratorTest(unittest.TestCase):
    def test_proto_generator(self):
        """
        [XOS-GenX] Generate DJANGO models, verify Fields and Foreign Keys
        """
        args = FakeArgs()
        args.files = [VROUTER_XPROTO]
        args.target = 'django.xtarget'
        output = XOSGenerator.generate(args)

        fields = filter(lambda s:'Field(' in s, output.splitlines())
        self.assertEqual(len(fields), 2)
        links = filter(lambda s:'Key(' in s, output.splitlines())
        self.assertEqual(len(links), 2)

if __name__ == '__main__':
    unittest.main()


