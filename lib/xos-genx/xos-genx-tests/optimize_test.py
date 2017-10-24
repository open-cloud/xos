
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
from xosgenx.jinja2_extensions.fol2 import FOL2Python

class XProtoOptimizeTest(unittest.TestCase):
    def setUp(self):
        self.f2p = FOL2Python()
        self.maxDiff=None

    def test_constant(self):
        input = 'True'
        output = self.f2p.hoist_outer(input)
        self.assertEqual(output, input)

    def test_exists(self):
        input = {'exists': ['X',{'|':['X.foo','y']}]}

        output = self.f2p.hoist_outer(input)
        expected = {'|': ['y', {'&': [{'not': 'y'}, {'exists': ['X', 'X.foo']}]}]}
        self.assertEqual(output, expected)
        
    def test_exists_implies(self):
        input = {'exists': ['Foo', {'&': [{'=': ('Foo.a', '1')}, {'->': ['write_access', {'=': ('Foo.b', '1')}]}]}]}

        output = self.f2p.hoist_outer(input)
        expected = {'|': [{'&': ['write_access', {'exists': ['Foo', {'&': [{'=': ['Foo.a', '1']}, {'=': ['Foo.b', '1']}]}]}]}, {'&': [{'not': 'write_access'}, {'exists': ['Foo', {'=': ['Foo.a', '1']}]}]}]}
        self.assertEqual(output, expected)

    def test_forall(self):
        input = {'forall': ['X',{'|':['X.foo','y']}]}

        output = self.f2p.hoist_outer(input)
        expected = {'|': ['y', {'&': [{'not': 'y'}, {'forall': ['X', 'X.foo']}]}]}
        self.assertEqual(output, expected)

    def test_exists_embedded(self):
        input = {'&':['True',{'exists': ['X',{'|':['X.foo','y']}]}]}

        output = self.f2p.hoist_outer(input)
        expected = {'|': ['y', {'&': [{'not': 'y'}, {'exists': ['X', 'X.foo']}]}]}
        self.assertEqual(output, expected)
    
    def test_exists_equals(self):
        input = {'&':['True',{'exists': ['X',{'|':['X.foo',{'=':['y','z']}]}]}]}

        output = self.f2p.hoist_outer(input)
        expected = {'|': [{'=': ['y', 'z']}, {'&': [{'not': {'=': ['y', 'z']}}, {'exists': ['X', 'X.foo']}]}]}
        self.assertEqual(output, expected)

    def test_exists_nested_constant(self):
        input = {'&':['True',{'exists': ['X',{'|':['y',{'=':['y','X.foo']}]}]}]}

        output = self.f2p.hoist_outer(input)
        expected = {'|': ['y', {'&': [{'not': 'y'}, {'exists': ['X', {'=': ['False', 'X.foo']}]}]}]}
        self.assertEqual(output, expected)

    def test_exists_nested(self):
        input = {'exists': ['X',{'exists':['Y',{'=':['Y.foo','X.foo']}]}]}

        output = self.f2p.hoist_outer(input)
        expected = input
        self.assertEqual(input, output)

    def test_exists_nested2(self):
        input = {'exists': ['X',{'exists':['Y',{'=':['Z','Y']}]}]}

        output = self.f2p.hoist_outer(input)
        expected = {'exists': ['Y', {'=': ['Z', 'Y']}]}
        self.assertEqual(output, expected)

    def test_exists_nested3(self):
        input = {'exists': ['X',{'exists':['Y',{'=':['Z','X']}]}]}

        output = self.f2p.hoist_outer(input)
        expected = {'exists': ['X', {'=': ['Z', 'X']}]}
        self.assertEqual(output, expected)


if __name__ == '__main__':
    unittest.main()


