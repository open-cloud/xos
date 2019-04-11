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
from helpers import OUTPUT_DIR
from xosgenx.generator import XOSProcessor, XOSProcessorArgs

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

BASE_XPROTO = os.path.abspath(
    os.path.dirname(os.path.realpath(__file__)) + "/xproto/base.xproto"
)
TEST_XPROTO = os.path.abspath(
    os.path.dirname(os.path.realpath(__file__)) + "/xproto/test.xproto"
)
FIELDTEST_XPROTO = os.path.abspath(
    os.path.dirname(os.path.realpath(__file__)) + "/xproto/fieldtest.xproto"
)
REVERSEFIELDTEST_XPROTO = os.path.abspath(
    os.path.dirname(os.path.realpath(__file__)) + "/xproto/reversefieldtest.xproto"
)
FILTERTEST_XPROTO = os.path.abspath(
    os.path.dirname(os.path.realpath(__file__)) + "/xproto/filtertest.xproto"
)
CUSTOM_TEST1_XPROTO = os.path.abspath(
    os.path.dirname(os.path.realpath(__file__)) + "/xproto/custom_test1.xproto"
)
CUSTOM_TEST2_XPROTO = os.path.abspath(
    os.path.dirname(os.path.realpath(__file__)) + "/xproto/custom_test2.xproto"
)
SKIP_DJANGO_XPROTO = os.path.abspath(
    os.path.dirname(os.path.realpath(__file__)) + "/xproto/skip_django.xproto"
)
VROUTER_XPROTO = os.path.abspath(
    os.path.dirname(os.path.realpath(__file__)) + "/xproto/vrouterport.xproto"
)
TEST_TARGET = os.path.abspath(
    os.path.dirname(os.path.realpath(__file__)) + "/xtarget/test.xtarget"
)
FIELDTEST_TARGET = os.path.abspath(
    os.path.dirname(os.path.realpath(__file__)) + "/xtarget/fieldtest.xtarget"
)
FILTERTEST_TARGET = os.path.abspath(
    os.path.dirname(os.path.realpath(__file__)) + "/xtarget/filtertest.xtarget"
)
SPLIT_TARGET = os.path.abspath(
    os.path.dirname(os.path.realpath(__file__)) + "/xtarget/split.xtarget"
)

TEST_ATTICS = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + "/attics/")


class XOSProcessorTest(unittest.TestCase):
    """
    Testing the XOS Generative Toolchain
    """

    def setUp(self):
        os.chdir(
            os.path.join(
                os.path.abspath(os.path.dirname(os.path.realpath(__file__))), ".."
            )
        )
        filesToRemove = [f for f in os.listdir(OUTPUT_DIR)]
        for f in filesToRemove:
            if not f.startswith("."):
                os.remove(OUTPUT_DIR + "/" + f)

    def test_generator_custom_target_from_file(self):
        """
        [XOS-GenX] Generate output from base.xproto
        """
        args = XOSProcessorArgs(files=[TEST_XPROTO], target=TEST_TARGET)
        output = XOSProcessor.process(args)
        self.assertEqual(output, TEST_EXPECTED_OUTPUT)

    def test_generator_custom_target_from_inputs(self):
        """
        [XOS-GenX] Generate output from base.xproto
        """
        args = XOSProcessorArgs(inputs=open(TEST_XPROTO).read(), target=TEST_TARGET)
        output = XOSProcessor.process(args)
        self.assertEqual(output, TEST_EXPECTED_OUTPUT)

    def test_django_with_attic(self):
        """
        [XOS-GenX] Generate django output from test.xproto
        """
        args = XOSProcessorArgs(
            files=[TEST_XPROTO, VROUTER_XPROTO],
            target="django.xtarget",
            attic=TEST_ATTICS,
            output=OUTPUT_DIR,
            dest_extension="py",
            write_to_file="model",
        )
        output = XOSProcessor.process(args)

        # xosmodel has custom header attic
        self.assertIn("from core.models.xosbase import *", output["XOSModel"])
        self.assertIn("class XOSModel_decl(XOSBase):", output["XOSModel"])

        # vrouter port use the default header
        self.assertIn("from core.models.xosbase import *", output["VRouterPort"])
        self.assertIn("class VRouterPort_decl(XOSBase):", output["VRouterPort"])

        # verify files
        xosmodel = OUTPUT_DIR + "/xosmodel.py"
        self.assertTrue(os.path.isfile(xosmodel))
        xmf = open(xosmodel).read()
        self.assertIn("from core.models.xosbase import *", xmf)
        self.assertIn("class XOSModel_decl(XOSBase):", xmf)

        vrouterport = OUTPUT_DIR + "/vrouterport.py"
        self.assertTrue(os.path.isfile(vrouterport))
        vrpf = open(vrouterport).read()
        self.assertIn("from core.models.xosbase import *", vrpf)
        self.assertIn("class VRouterPort_decl(XOSBase):", vrpf)

    def test_django_with_base(self):
        args = XOSProcessorArgs(
            files=[TEST_XPROTO, BASE_XPROTO],
            target="django.xtarget",
            attic=TEST_ATTICS,
            output=OUTPUT_DIR,
            dest_extension="py",
            write_to_file="model",
        )
        output = XOSProcessor.process(args)

        # verify files
        xosmodel = OUTPUT_DIR + "/xosmodel.py"
        self.assertTrue(os.path.isfile(xosmodel))
        xmf = open(xosmodel).read()
        self.assertIn("from core.models.xosbase import *", xmf)
        self.assertIn("class XOSModel_decl(XOSBase):", xmf)

        xosbase = OUTPUT_DIR + "/xosbase.py"
        self.assertTrue(os.path.isfile(xosbase))
        xbf = open(xosbase).read()
        self.assertIn("from core.models.xosbase import *", xbf)
        self.assertIn("class XOSBase_decl(models.Model, PlModelMixIn):", xbf)

    def test_write_multiple_files(self):
        """
        [XOS-GenX] read multiple models as input, print one file per model
        """
        args = XOSProcessorArgs(
            files=[TEST_XPROTO, VROUTER_XPROTO],
            target=TEST_TARGET,
            output=OUTPUT_DIR,
            dest_extension="txt",
            write_to_file="model",
        )
        XOSProcessor.process(args)

        generated_files = [f for f in os.listdir(OUTPUT_DIR) if not f.startswith(".")]
        self.assertEqual(len(generated_files), 2)

        xosmodel = open(os.path.join(OUTPUT_DIR, "xosmodel.txt"), "r").read()
        vrouterport = open(os.path.join(OUTPUT_DIR, "vrouterport.txt"), "r").read()

        self.assertIn("name: XOSModel", xosmodel)
        self.assertIn("name: VRouterPort", vrouterport)

    def test_write_multiple_files_from_xtarget(self):
        """
        [XOS-GenX] read multiple models as input, print separate files based on +++
        """
        args = XOSProcessorArgs(
            files=[TEST_XPROTO, VROUTER_XPROTO],
            target=SPLIT_TARGET,
            output=OUTPUT_DIR,
            write_to_file="target",
        )
        XOSProcessor.process(args)

        generated_files = [f for f in os.listdir(OUTPUT_DIR) if not f.startswith(".")]
        self.assertEqual(len(generated_files), 2)

        xosmodel = open(os.path.join(OUTPUT_DIR, "xosmodel.txt"), "r").read()
        vrouterport = open(os.path.join(OUTPUT_DIR, "vrouterport.txt"), "r").read()

        self.assertIn("name: XOSModel", xosmodel)
        self.assertIn("name: VRouterPort", vrouterport)

    def test_skip_django(self):
        args = XOSProcessorArgs(
            files=[SKIP_DJANGO_XPROTO],
            target="django.xtarget",
            output=OUTPUT_DIR,
            dest_extension="py",
            write_to_file="model",
        )
        output = XOSProcessor.process(args)

        # should not print a file if options.skip_django = True
        file = OUTPUT_DIR + "/user.py"
        self.assertFalse(os.path.isfile(file))

    def test_service_order(self):
        args = XOSProcessorArgs(
            files=[BASE_XPROTO, TEST_XPROTO, VROUTER_XPROTO],
            target="service.xtarget",
            output=OUTPUT_DIR,
            write_to_file="target",
        )
        output = XOSProcessor.process(args)

        model = OUTPUT_DIR + "/models.py"
        self.assertTrue(os.path.isfile(model))
        line_num = 0

        for line in open(model).readlines():
            line_num += 1
            if line.find("class XOSBase(models.Model, PlModelMixIn):") >= 0:
                base_line = line_num
            if line.find("XOSModel(XOSBase):") >= 0:
                xosmodel_line = line_num
            if line.find("class VRouterPort(XOSBase):") >= 0:
                vrouter_line = line_num
        self.assertLess(base_line, xosmodel_line)
        self.assertLess(xosmodel_line, vrouter_line)

    def test_field_numbers(self):
        args = XOSProcessorArgs(files=[FIELDTEST_XPROTO], target=FIELDTEST_TARGET)
        output = XOSProcessor.process(args)

        def _assert_field(modelname, fieldname, id):
            self.assertIn("%s,%s,%s" % (modelname, fieldname, id), output)

        _assert_field("Site", "id", 1)
        _assert_field("Site", "base_field", 2)
        _assert_field("Site", "base_field2", 3)
        _assert_field("Site", "otherstuff_field", 102)
        _assert_field("Site", "slice_field", 201)
        _assert_field("Site", "slices_ids", 1002)

        _assert_field("Slice", "id", 1)
        _assert_field("Slice", "base_field", 2)
        _assert_field("Slice", "base_field2", 3)
        _assert_field("Slice", "slice_field", 101)
        _assert_field("Slice", "site", 102)

    def test_field_numbers(self):
        args = XOSProcessorArgs(
            files=[REVERSEFIELDTEST_XPROTO], target=FIELDTEST_TARGET
        )
        output = XOSProcessor.process(args)

        def _assert_field(modelname, fieldname, id):
            self.assertIn("%s,%s,%s" % (modelname, fieldname, id), output)

        # rel_int1s_ids is the reverse link from RelatedToIntermediate1. It gets the related id with no offset, so it
        # will be assigned 1001. rel_leaf1as_ids inherits from Intermediate1, so its reverse links will all be offset
        # by 100
        _assert_field("Leaf1a", "rel_int1s_ids", 1001)
        _assert_field("Leaf1a", "rel_leaf1as_ids", 1101)

        # rel_int2s_ids is the reverse link from RelatedToIntermediate1. It gets the related id with no offset, so it
        # will be assigned 1001. rel_leaf1bs_ids inherits from Intermediate1, so its reverse links will all be offset
        # by 100
        _assert_field("Leaf1b", "rel_int1s_ids", 1001)
        _assert_field("Leaf1b", "rel_leaf1bs_ids", 1101)

        # There are no reverse numbers specified for Intermediate2 or Leaf2, so xproto will fall back to automatic
        # numbering starting at 1900.
        _assert_field("Leaf2", "rel_int2s_ids", 1900)
        _assert_field("Leaf2", "rel_leaf2s_ids", 1901)

    def test_unfiltered(self):
        """ With no include_* args, should get all models """
        args = XOSProcessorArgs(files=[FILTERTEST_XPROTO], target=FILTERTEST_TARGET)
        output = XOSProcessor.process(args)

        self.assertEqual(output, "Model1,Model2,Model3,")

    def test_filter_models(self):
        """ Should only get models specified by include_models """
        args = XOSProcessorArgs(
            files=[FILTERTEST_XPROTO],
            target=FILTERTEST_TARGET,
            include_models=["Model1", "Model3"],
        )
        output = XOSProcessor.process(args)

        self.assertEqual(output, "Model1,Model3,")

    def test_filter_apps(self):
        """ Should only get models whose apps are specified by include_apps """
        args = XOSProcessorArgs(
            files=[FILTERTEST_XPROTO], target=FILTERTEST_TARGET, include_apps=["core"]
        )
        output = XOSProcessor.process(args)

        self.assertEqual(output, "Model1,Model2,")

    def test_django_custom_test1(self):
        args = XOSProcessorArgs(
            files=[CUSTOM_TEST1_XPROTO, BASE_XPROTO],
            target="django.xtarget",
            attic=TEST_ATTICS,
            output=OUTPUT_DIR,
            dest_extension="py",
            write_to_file="model",
        )
        output = XOSProcessor.process(args)

        # verify files
        xosmodel = OUTPUT_DIR + "/xosmodel_decl.py"
        self.assertTrue(os.path.isfile(xosmodel))
        xmf = open(xosmodel).read()
        self.assertIn("class XOSModel_decl(XOSBase):", xmf)

        xosmodel = OUTPUT_DIR + "/xosmodel2_decl.py"
        self.assertTrue(os.path.isfile(xosmodel))
        xmf = open(xosmodel).read()
        self.assertIn("class XOSModel2_decl(XOSBase):", xmf)

    def test_django_custom_test2(self):
        args = XOSProcessorArgs(
            files=[CUSTOM_TEST2_XPROTO, BASE_XPROTO],
            target="django.xtarget",
            attic=TEST_ATTICS,
            output=OUTPUT_DIR,
            dest_extension="py",
            write_to_file="model",
        )
        output = XOSProcessor.process(args)

        # verify files
        xosmodel = OUTPUT_DIR + "/xosmodel_decl.py"
        self.assertTrue(os.path.isfile(xosmodel))
        xmf = open(xosmodel).read()
        self.assertIn("class XOSModel_decl(XOSBase):", xmf)
        self.assertNotIn("class XOSModel(XOSModel_decl):", xmf)

        xosmodel = OUTPUT_DIR + "/xosmodel2.py"
        self.assertTrue(os.path.isfile(xosmodel))
        xmf = open(xosmodel).read()
        self.assertIn("class XOSModel2_decl(XOSBase):", xmf)
        self.assertIn("class XOSModel2(XOSModel2_decl):", xmf)

    def test_service_custom_test1(self):
        args = XOSProcessorArgs(
            files=[CUSTOM_TEST1_XPROTO, BASE_XPROTO],
            target="service.xtarget",
            attic=TEST_ATTICS,
            output=OUTPUT_DIR,
            dest_extension="py",
            write_to_file="target",
        )
        output = XOSProcessor.process(args)

        # verify files
        xosmodel = OUTPUT_DIR + "/models_decl.py"
        self.assertTrue(os.path.isfile(xosmodel))
        xmf = open(xosmodel).read()
        self.assertIn("class XOSModel_decl(XOSBase_decl):", xmf)

        xosmodel = OUTPUT_DIR + "/models_decl.py"
        self.assertTrue(os.path.isfile(xosmodel))
        xmf = open(xosmodel).read()
        self.assertIn("class XOSModel2_decl(XOSBase_decl):", xmf)


if __name__ == "__main__":
    unittest.main()
