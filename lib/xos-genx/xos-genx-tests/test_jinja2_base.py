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
from xosgenx.jinja2_extensions.base import *


# Several of the base functions require a Field object.
def _field(name, singular=None, plural=None):
    f = {}
    f["name"] = name
    f["options"] = {}
    if singular:
        f["options"]["singular"] = singular
    if plural:
        f["options"]["plural"] = plural
    return f


class Jinja2BaseTests(unittest.TestCase):
    def test_xproto_is_true(self):
        self.assertTrue(xproto_is_true(True))
        self.assertTrue(xproto_is_true("True"))
        self.assertTrue(xproto_is_true('"True"'))
        self.assertFalse(xproto_is_true(False))
        self.assertFalse(xproto_is_true("False"))
        self.assertFalse(xproto_is_true('"False"'))
        self.assertFalse(xproto_is_true(None))
        self.assertFalse(xproto_is_true("something else"))

    def test_unquote(self):
        self.assertEqual(xproto_unquote("foo"), "foo")
        self.assertEqual(xproto_unquote('"foo"'), "foo")

    def test_pluralize(self):
        self.assertEqual(xproto_pluralize(_field("sheep")), "sheep")
        self.assertEqual(xproto_pluralize(_field("slice")), "slices")
        self.assertEqual(xproto_pluralize(_field("network")), "networks")
        self.assertEqual(xproto_pluralize(_field("omf_friendly")), "omf_friendlies")
        # invalid words, should usually return <word>-es
        self.assertEqual(xproto_pluralize(_field("xxx")), "xxxes")
        # if a field option is set, use that
        self.assertEqual(xproto_pluralize(_field("sheep", plural="turtles")), "turtles")

    def test_singularize(self):
        self.assertEqual(xproto_singularize(_field("sheep")), "sheep")
        self.assertEqual(xproto_singularize(_field("slices")), "slice")
        self.assertEqual(xproto_singularize(_field("networks")), "network")
        self.assertEqual(xproto_singularize(_field("omf_friendlies")), "omf_friendly")
        # invalid words, return the original word
        self.assertEqual(xproto_singularize(_field("xxx")), "xxx")
        # if a field option is set, use that
        self.assertEqual(xproto_pluralize(_field("sheep", plural="turtles")), "turtles")

    def test_singularize_pluralize(self):
        self.assertEqual(xproto_singularize_pluralize(_field("sheep")), "sheep")
        self.assertEqual(xproto_singularize_pluralize(_field("slices")), "slices")
        self.assertEqual(xproto_singularize_pluralize(_field("networks")), "networks")
        self.assertEqual(
            xproto_singularize_pluralize(_field("omf_friendlies")), "omf_friendlies"
        )
        # invalid words, should usually return <word>-es
        self.assertEqual(xproto_singularize_pluralize(_field("xxx")), "xxxes")
        # if a field option is set, use that
        self.assertEqual(
            xproto_singularize(_field("sheep", singular="turtle")), "turtle"
        )


if __name__ == "__main__":
    unittest.main()
