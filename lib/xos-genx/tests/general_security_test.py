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
class XProtoSecurityTest(unittest.TestCase):
    def setUp(self):
        self.target = XProtoTestHelpers.write_tmp_target("""
{% for name, policy in proto.policies.items() %}
{{ xproto_fol_to_python_test(name, policy, None, '0') }}
{% endfor %}
""")

    def test_constant(self):
        xproto = \
"""
    policy output < True >
"""
        args = FakeArgs()
        args.inputs = xproto
        args.target = self.target

        output = XOSGenerator.generate(args)

        exec(output) # This loads the generated function, which should look like this:

        """
        def policy_output_enforcer(obj, ctx):
            i1 = True
            return i1
        """

        verdict = policy_output_enforcer({}, {})
        self.assertTrue(verdict)

    def test_equal(self):
        xproto = \
"""
    policy output < ctx.user = obj.user >
"""

        args = FakeArgs()
        args.inputs = xproto
        args.target = self.target

        output = XOSGenerator.generate(args)

        exec(output) # This loads the generated function, which should look like this:

        """
        def policy_output_enforcer(obj, ctx):
            i1 = (ctx.user == obj.user)
            return i1
        """

        obj = FakeArgs()
	obj.user = 1
        ctx = FakeArgs()
	ctx.user = 1

        verdict = policy_output_enforcer(obj, ctx)

    def test_call_policy(self):
        xproto = \
"""
    policy sub_policy < ctx.user = obj.user >
    policy output < *sub_policy(child) >
"""

        args = FakeArgs()
        args.inputs = xproto
        args.target = self.target

        output = XOSGenerator.generate(args)

        exec(output,globals()) # This loads the generated function, which should look like this:

        """
        def policy_sub_policy_enforcer(obj, ctx):
            i1 = (ctx.user == obj.user)
    	    return i1

	def policy_output_enforcer(obj, ctx):
	    i1 = policy_sub_policy_enforcer(obj.child, ctx)
	    return i1
        """

        obj = FakeArgs()
        obj.child = FakeArgs()
	obj.child.user = 1

        ctx = FakeArgs()
	ctx.user = 1

        verdict = policy_output_enforcer(obj, ctx)
        self.assertTrue(verdict)


    def test_bin(self):
        xproto = \
"""
    policy output < ctx.is_admin = True | obj.empty = True>
"""

        args = FakeArgs()
        args.inputs = xproto
        args.target = self.target

        output = XOSGenerator.generate(args)
        exec(output) # This loads the generated function, which should look like this:

        """
	def policy_output_enforcer(obj, ctx):
	    i2 = (ctx.is_admin == True)
	    i3 = (obj.empty == True)
	    i1 = (i2 or i3)
	    return i1
        """

        obj = FakeArgs()
	obj.empty = True

	ctx = FakeArgs()
	ctx.is_admin = True

        verdict = policy_output_enforcer(obj, ctx)

        self.assertTrue(verdict)

        
    def test_exists(self):
        xproto = \
"""
    policy output < exists Privilege: Privilege.object_id = obj.id >
"""
	args = FakeArgs()
        args.inputs = xproto
        args.target = self.target

        output = XOSGenerator.generate(args)
        exec(output) # This loads the generated function, which should look like this:

        """
	def policy_output_enforcer(obj, ctx):
	    i1 = Privilege.objects.filter(object_id=obj.id)
    	    return i1
        """

        self.assertTrue(policy_output_enforcer is not None)
	
    def test_python(self):
        xproto = \
"""
    policy output < {{ "jack" in ["the", "box"] }} = False >
"""
	args = FakeArgs()
        args.inputs = xproto
        args.target = self.target
        output = XOSGenerator.generate(args)
        exec(output) # This loads the generated function, which should look like this:

        """
        def policy_output_enforcer(obj, ctx):
            i2 = ('jack' in ['the', 'box'])
            i1 = (i2 == False)
            return i1
        """

        self.assertTrue(policy_output_enforcer({}, {}) is True)

    def test_forall(self):
        # This one we only parse
        xproto = \
"""
    policy output < forall Credential: Credential.obj_id = obj_id >
"""

        args = FakeArgs()
        args.inputs = xproto
        args.target = self.target

        output = XOSGenerator.generate(args)
        """
        def policy_output_enforcer(obj, ctx):
            i2 = Credential.objects.filter((~ Q(obj_id=obj_id)))[0]
            i1 = (not i2)
            return i1
        """
        exec(output)

if __name__ == '__main__':
    unittest.main()
