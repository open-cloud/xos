
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
from helpers import FakeArgs, OUTPUT_DIR
from xosgenx.generator import XOSGenerator

TEST_EXPECTED_OUTPUT = """
    name: XOSModel
    fields:
            name:
                type: string
                description: "Help Name"
            files:
                type: string
                description: "Help Files"
"""

BASE_XPROTO = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + "/xproto/base.xproto")
TEST_XPROTO = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + "/xproto/test.xproto")
SKIP_DJANGO_XPROTO = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + "/xproto/skip_django.xproto")
VROUTER_XPROTO = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + "/xproto/vrouterport.xproto")
TEST_TARGET = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + "/xtarget/test.xtarget")
SPLIT_TARGET = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + "/xtarget/split.xtarget")

TEST_ATTICS = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + "/attics/")

class XOSGeneratorTest(unittest.TestCase):
    """
    Testing the XOS Generative Toolchain
    """

    def setUp(self):
        filesToRemove = [f for f in os.listdir(OUTPUT_DIR)]
        for f in filesToRemove:
            if not f.startswith('.'):
                os.remove(OUTPUT_DIR + '/' + f)

    def test_generator_custom_target_from_file(self):
        """
        [XOS-GenX] Generate output from base.xproto
        """
        args = FakeArgs()
        args.files = [TEST_XPROTO]
        args.target = TEST_TARGET
        output = XOSGenerator.generate(args)
        self.assertEqual(output, TEST_EXPECTED_OUTPUT)

    def test_generator_custom_target_from_inputs(self):
        """
        [XOS-GenX] Generate output from base.xproto
        """
        args = FakeArgs()
        args.inputs = open(TEST_XPROTO).read()
        args.target = TEST_TARGET
        output = XOSGenerator.generate(args)
        self.assertEqual(output, TEST_EXPECTED_OUTPUT)

    def test_django_with_attic(self):
        """
        [XOS-GenX] Generate django output from test.xproto
        """
        args = FakeArgs()
        args.files = [TEST_XPROTO, VROUTER_XPROTO]
        args.target = 'django.xtarget'
        args.attic = TEST_ATTICS
        args.output = OUTPUT_DIR
        args.dest_extension = 'py'
        args.write_to_file = 'model'
        output = XOSGenerator.generate(args)

        # xosmodel has custom header attic
        self.assertIn('from xosmodel_header import *', output['XOSModel'])
        self.assertIn('class XOSModel(XOSBase):', output['XOSModel'])

        # vrouter port use the default header
        self.assertIn('header import *', output['VRouterPort'])
        self.assertIn('class VRouterPort(XOSBase):', output['VRouterPort'])

        #verify files
        xosmodel = OUTPUT_DIR + '/xosmodel.py'
        self.assertTrue(os.path.isfile(xosmodel))
        xmf = open(xosmodel).read()
        self.assertIn('from xosmodel_header import *', xmf)
        self.assertIn('class XOSModel(XOSBase):', xmf)

        vrouterport = OUTPUT_DIR + '/vrouterport.py'
        self.assertTrue(os.path.isfile(vrouterport))
        vrpf = open(vrouterport).read()
        self.assertIn('header import *', vrpf)
        self.assertIn('class VRouterPort(XOSBase):', vrpf)

    def test_django_with_base(self):
        args = FakeArgs()
        args.files = [TEST_XPROTO, BASE_XPROTO]
        args.target = 'django.xtarget'
        args.attic = TEST_ATTICS
        args.output = OUTPUT_DIR
        args.dest_extension = 'py'
        args.write_to_file = 'model'
        output = XOSGenerator.generate(args)

        # verify files
        xosmodel = OUTPUT_DIR + '/xosmodel.py'
        self.assertTrue(os.path.isfile(xosmodel))
        xmf = open(xosmodel).read()
        self.assertIn('from xosmodel_header import *', xmf)
        self.assertIn('class XOSModel(XOSBase):', xmf)

        xosbase = OUTPUT_DIR + '/xosbase.py'
        self.assertTrue(os.path.isfile(xosbase))
        xbf = open(xosbase).read()
        self.assertIn('header import *', xbf)
        self.assertIn('class XOSBase(models.Model, PlModelMixIn):', xbf)

    def test_write_multiple_files(self):
        """
        [XOS-GenX] read multiple models as input, print one file per model
        """
        args = FakeArgs()
        args.files = [TEST_XPROTO, VROUTER_XPROTO]
        args.target = TEST_TARGET
        args.output = OUTPUT_DIR
        args.dest_extension = 'txt'
        args.write_to_file = 'model'
        XOSGenerator.generate(args)

        generated_files = [f for f in os.listdir(OUTPUT_DIR) if not f.startswith('.')]
        self.assertEqual(len(generated_files), 2)

        xosmodel = open(os.path.join(OUTPUT_DIR, 'xosmodel.txt'), "r").read()
        vrouterport = open(os.path.join(OUTPUT_DIR, 'vrouterport.txt'), "r").read()

        self.assertIn("name: XOSModel", xosmodel)
        self.assertIn("name: VRouterPort", vrouterport)

    def test_write_multiple_files_from_xtarget(self):
        """
        [XOS-GenX] read multiple models as input, print separate files based on +++
        """
        args = FakeArgs()
        args.files = [TEST_XPROTO, VROUTER_XPROTO]
        args.target = SPLIT_TARGET
        args.output = OUTPUT_DIR
        args.write_to_file = 'target'
        XOSGenerator.generate(args)

        generated_files = [f for f in os.listdir(OUTPUT_DIR) if not f.startswith('.')]
        self.assertEqual(len(generated_files), 2)

        xosmodel = open(os.path.join(OUTPUT_DIR, 'xosmodel.txt'), "r").read()
        vrouterport = open(os.path.join(OUTPUT_DIR, 'vrouterport.txt'), "r").read()

        self.assertIn("name: XOSModel", xosmodel)
        self.assertIn("name: VRouterPort", vrouterport)

    def test_skip_django(self):
        args = FakeArgs()
        args.files = [SKIP_DJANGO_XPROTO]
        args.target = 'django.xtarget'
        args.output = OUTPUT_DIR
        args.dest_extension = 'py'
        args.write_to_file = 'model'
        output = XOSGenerator.generate(args)

        # should not print a file if options.skip_django = True
        file = OUTPUT_DIR + '/user.py'
        self.assertFalse(os.path.isfile(file))

    def test_service_order(self):
        args = FakeArgs()
        args.files = [BASE_XPROTO, TEST_XPROTO, VROUTER_XPROTO]
        args.target = 'service.xtarget'
        args.output = OUTPUT_DIR
        args.write_to_file = 'target'
        output = XOSGenerator.generate(args)

        model = OUTPUT_DIR + '/models.py'
        self.assertTrue(os.path.isfile(model))
        line_num = 0

        for line in open(model).readlines():
            line_num += 1
            if line.find('class XOSBase(models.Model, PlModelMixIn):') >= 0:
                base_line = line_num
            if line.find('XOSModel(XOSBase):') >= 0:
                xosmodel_line = line_num
            if line.find('class VRouterPort(XOSBase):') >= 0:
                vrouter_line = line_num
        self.assertLess(base_line, xosmodel_line)
        self.assertLess(xosmodel_line, vrouter_line)


if __name__ == '__main__':
    unittest.main()
