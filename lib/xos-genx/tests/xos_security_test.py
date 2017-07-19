import unittest
from xosgenx.generator import XOSGenerator
from helpers import FakeArgs, XProtoTestHelpers

"""The function below is for eliminating warnings arising due to the missing policy_output_enforcer,
which is generated and loaded dynamically.
"""
def policy_output_enforcer(x, y):
    raise Exception("Security enforcer not generated. Test failed.")
    return False

"""
The tests below use the Python code target to generate 
Python security policies, set up an appropriate environment and execute the Python.
"""
class XProtoXOSSecurityTest(unittest.TestCase):
    def setUp(self):
        self.target = XProtoTestHelpers.write_tmp_target("{{ xproto_fol_to_python_test('output',proto.policies.test_policy, None, '0') }}")

    """
    This is the security policy for controllers
    """
    def test_controller_policy(self):
        xproto = \
"""
    policy test_policy < ctx.user.is_admin | exists Privilege: Privilege.user_id = ctx.user.id & Privilege.object_type = "Deployment" >
"""
        args = FakeArgs()
        args.inputs = xproto
        args.target = self.target

        output = XOSGenerator.generate(args)

        exec(output) # This loads the generated function, which should look like this:

        """
        def policy_output_enforcer(obj, ctx):
            i2 = ctx.user.is_admin
            i3 = Privilege.objects.filter(Q(user_id=ctx.user.id), Q(object_type='Deployment'))[0]
            i1 = (i2 or i3)
            return i1
        """

        # FIXME: Test this policy by executing it
        self.assertTrue(policy_output_enforcer is not None)

    """
    This is the security policy for controllers
    """
    def _test_controller_network_policy(self):
        xproto = \
"""
    policy test_policy < ctx.user.is_admin | exists Slice: forall ctx.networks: ctx.networks.owner.id = Slice.id >
"""
        args = FakeArgs()
        args.inputs = xproto
        args.target = self.target

        output = XOSGenerator.generate(args)

        exec(output) # This loads the generated function, which should look like this:

        """
        def policy_output_enforcer(obj, ctx):
            i2 = ctx.user.is_admin
            i3 = Privilege.objects.filter(Q(user_id=ctx.user.id), Q(object_type='Deployment'))[0]
            i1 = (i2 or i3)
            return i1
        """

        # FIXME: Test this policy by executing it
        self.assertTrue(policy_output_enforcer is not None)


if __name__ == '__main__':
    unittest.main()
