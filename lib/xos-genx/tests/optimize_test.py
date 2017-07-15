import unittest
from xosgenx.jinja2_extensions.fol2 import FOL2Python
import pdb

class XProtoOptimizeTest(unittest.TestCase):
    def setUp(self):
        self.f2p = FOL2Python()

    def test_constant(self):
        input = 'True'
        output = self.f2p.hoist_constants(input)
        self.assertEqual(output, input)

    def test_exists(self):
        input = {'exists': ['x',{'|':['x','y']}]}

        output = self.f2p.hoist_constants(input)
        expected = {'|': ['y', {'exists': ['x', 'x']}]}
        self.assertEqual(output, expected)
        
    def test_forall(self):
        input = {'forall': ['x',{'|':['x','y']}]}

        output = self.f2p.hoist_constants(input)
        expected = {'|': ['y', {'forall': ['x', 'x']}]}
        self.assertEqual(output, expected)

    def test_exists_embedded(self):
        input = {'|':['True',{'exists': ['x',{'|':['x','y']}]}]}

        output = self.f2p.hoist_constants(input)
        expected = {'|': ['True', {'|': ['y', {'exists': ['x', 'x']}]}]}
        self.assertEqual(output, expected)
    
    def test_exists_equals(self):
        input = {'|':['True',{'exists': ['x',{'|':['x',{'=':['y','z']}]}]}]}

        output = self.f2p.hoist_constants(input)
        expected = {'|': ['True', {'|': [{'=': ['y', 'z']}, {'exists': ['x', 'x']}]}]}
        self.assertEqual(output, expected)

    def test_exists_nested_constant(self):
        input = {'|':['True',{'exists': ['x',{'|':['y',{'=':['y','x']}]}]}]}

        output = self.f2p.hoist_constants(input)
        expected = {'|': ['True', {'|': ['y', {'exists': ['x', {'=': ['y', 'x']}]}]}]}
        self.assertEqual(output, expected)

    def test_exists_nested(self):
        input = {'exists': ['x',{'exists':['y',{'=':['y','x']}]}]}

        output = self.f2p.hoist_constants(input)
        expected = {'exists': ['x', {'exists': ['y', {'=': ['y', 'x']}]}]}
        self.assertEqual(output, expected)

    def test_exists_nested2(self):
        input = {'exists': ['x',{'exists':['y',{'=':['z','y']}]}]}

        output = self.f2p.hoist_constants(input)
        expected = {'exists': ['y', {'=': ['z', 'y']}]}
        self.assertEqual(output, expected)

    def test_exists_nested3(self):
        input = {'exists': ['x',{'exists':['y',{'=':['z','x']}]}]}

        output = self.f2p.hoist_constants(input)
        expected = {'exists': ['x', {'=': ['z', 'x']}]}
        self.assertEqual(output, expected)


if __name__ == '__main__':
    unittest.main()


