import unittest
from xosgenx.generator import XOSGenerator
from helpers import FakeArgs, XProtoTestHelpers
import pdb

"""
The tests below convert the policy logic expression
into Python, set up an appropriate environment and execute the Python.
"""

class XProtoPolicyTest(unittest.TestCase):
    def test_constant(self):
        xproto = \
"""
    policy true_policy < True >
"""

        target = XProtoTestHelpers.write_tmp_target("{{ proto.policies.true_policy }}")

        args = FakeArgs()
        args.inputs = xproto
        args.target = target

        output = XOSGenerator.generate(args).replace('t','T')
        self.assertTrue(eval(output)) 

    def test_equal(self):
        xproto = \
"""
    policy slice_user < slice.user = obj.user >
"""

        target = XProtoTestHelpers.write_tmp_target("{{ proto.policies.slice_user }}")
        args = FakeArgs()
        args.inputs = xproto
        args.target = target

        output = XOSGenerator.generate(args)
       
        slice = FakeArgs()
        slice.user = 'twin'
        obj = FakeArgs()
        obj.user = 'twin'

        (op, operands), = eval(output).items()
        expr = op.join(operands).replace('=','==')

        self.assertTrue(eval(expr))

    def test_bin(self):
        xproto = \
"""
    policy slice_admin < slice.is_admin | obj.empty >
"""
        target = XProtoTestHelpers.write_tmp_target("{{ proto.policies.slice_admin }}")
        args = FakeArgs()
        args.inputs = xproto
        args.target = target

        output = XOSGenerator.generate(args)

        slice = FakeArgs()
        slice.is_admin = False
        obj = FakeArgs()
        obj.empty = []

        (op, operands), = eval(output).items()
        expr = op.join(operands).replace('|',' or ')

        self.assertFalse(eval(expr))

        
    def test_exists(self):
        xproto = \
"""
    policy privilege < exists Privilege: Privilege.object_id = obj.id >
"""

        target = XProtoTestHelpers.write_tmp_target("{{ proto.policies.privilege }} ")
        args = FakeArgs()
        args.inputs = xproto
        args.target = target

        output = XOSGenerator.generate(args)
        
        Privilege = FakeArgs()
        Privilege.object_id = 1
        obj = FakeArgs()
        obj.id = 1

        (op, operands), = eval(output).items()
        (op2, operands2), = operands[1].items()
        expr = op2.join(operands2).replace('=','==')

        self.assertTrue(eval(expr))

    def test_forall(self):
        # This one we only parse
        xproto = \
"""
    policy instance < forall Instance: exists Credential: Credential.obj_id = Instance.obj_id >
"""

        target = XProtoTestHelpers.write_tmp_target("{{ proto.policies.instance }}")

        args = FakeArgs()
        args.inputs = xproto
        args.target = target

        output = XOSGenerator.generate(args)
        (op, operands), = eval(output).items()

        self.assertEqual(op,'forall')


if __name__ == '__main__':
    unittest.main()


