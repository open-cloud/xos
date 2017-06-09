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


