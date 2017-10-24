
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
from xosgenx.generator import XOSGenerator
from helpers import FakeArgs, XProtoTestHelpers

"""The function below is for eliminating warnings arising due to the missing output_security_check,
which is generated and loaded dynamically.
"""
def output_security_check(x, y):
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
        def output_security_check(obj, ctx):
            i1 = True
            return i1
        """

        verdict = output_security_check({}, {})
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
        def output_security_check(obj, ctx):
            i1 = (ctx.user == obj.user)
            return i1
        """

        obj = FakeArgs()
	obj.user = 1
        ctx = FakeArgs()
	ctx.user = 1

        verdict = output_security_check(obj, ctx)

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
        def sub_policy_security_check(obj, ctx):
            i1 = (ctx.user == obj.user)
            return i1

        def output_security_check(obj, ctx):
            if obj.child:
		i1 = sub_policy_security_check(obj.child, ctx)
	    else:
		i1 = True
	    return i1
        """

        obj = FakeArgs()
        obj.child = FakeArgs()
	obj.child.user = 1

        ctx = FakeArgs()
	ctx.user = 1

        verdict = output_security_check(obj, ctx)
        self.assertTrue(verdict)

    def test_call_policy_child_none(self):
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
        def sub_policy_security_check(obj, ctx):
            i1 = (ctx.user == obj.user)
            return i1

        def output_security_check(obj, ctx):
            if obj.child:
		i1 = sub_policy_security_check(obj.child, ctx)
	    else:
		i1 = True
	    return i1
        """

        obj = FakeArgs()
        obj.child = None

        ctx = FakeArgs()
	ctx.user = 1

        verdict = output_security_check(obj, ctx)
        self.assertTrue(verdict)

    def test_call_policy_child_none(self):
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
        def sub_policy_security_check(obj, ctx):
            i1 = (ctx.user == obj.user)
            return i1

        def output_security_check(obj, ctx):
            if obj.child:
		i1 = sub_policy_security_check(obj.child, ctx)
	    else:
		i1 = True
	    return i1
        """

        obj = FakeArgs()
        obj.child = None

        ctx = FakeArgs()
	ctx.user = 1

        verdict = output_security_check(obj, ctx)
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
	def output_security_check(obj, ctx):
	    i2 = (ctx.is_admin == True)
	    i3 = (obj.empty == True)
	    i1 = (i2 or i3)
	    return i1
        """

        obj = FakeArgs()
	obj.empty = True

	ctx = FakeArgs()
	ctx.is_admin = True

        verdict = output_security_check(obj, ctx)

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
	def output_security_check(obj, ctx):
	    i1 = Privilege.objects.filter(object_id=obj.id)
    	    return i1
        """

        self.assertTrue(output_security_check is not None)
	
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
        def output_security_check(obj, ctx):
            i2 = ('jack' in ['the', 'box'])
            i1 = (i2 == False)
            return i1
        """

        self.assertTrue(output_security_check({}, {}) is True)

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
        def output_security_check(obj, ctx):
            i2 = Credential.objects.filter((~ Q(obj_id=obj_id)))[0]
            i1 = (not i2)
            return i1
        """
        exec(output)

if __name__ == '__main__':
    unittest.main()
