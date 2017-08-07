
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
import pdb

"""The function below is for eliminating warnings arising due to the missing policy_output_validator,
which is generated and loaded dynamically.
"""
def policy_output_validator(x, y):
    raise Exception("Validator not generated. Test failed.")
    return False

"""
The tests below use the Python code target to generate 
Python validation policies, set up an appropriate environment and execute the Python.
"""
class XProtoGeneralValidationTest(unittest.TestCase):
    def setUp(self):
        self.target = XProtoTestHelpers.write_tmp_target("""
{% for name, policy in proto.policies.items() %}
{{ xproto_fol_to_python_validator(name, policy, None, 'Necessary Failure') }}
{% endfor %}
""")

    def test_constant(self):
        xproto = \
"""
    policy output < False >
"""
        args = FakeArgs()
        args.inputs = xproto
        args.target = self.target

        output = XOSGenerator.generate(args)

        exec(output) # This loads the generated function, which should look like this:

        """
        def policy_output_validator(obj, ctx):
            i1 = False
            if (not i1):
                raise Exception('Necessary Failure')
        """

        with self.assertRaises(Exception):
           policy_output_validator({}, {})
    
    def test_equal(self):
        xproto = \
"""
    policy output < not (ctx.user = obj.user) >
"""

        args = FakeArgs()
        args.inputs = xproto
        args.target = self.target

        output = XOSGenerator.generate(args)

        exec(output) # This loads the generated function, which should look like this:

        """
        def policy_output_validator(obj, ctx):
            i2 = (ctx.user == obj.user)
            i1 = (not i2)
            if (not i1):
                raise Exception('Necessary Failure')
        """

        obj = FakeArgs()
	obj.user = 1
        ctx = FakeArgs()
	ctx.user = 1

        with self.assertRaises(Exception):
           policy_output_validator(obj, ctx)

    def test_equal(self):
        xproto = \
"""
    policy output < not (ctx.user = obj.user) >
"""

        args = FakeArgs()
        args.inputs = xproto
        args.target = self.target

        output = XOSGenerator.generate(args)

        exec(output) # This loads the generated function, which should look like this:

        """
        def policy_output_validator(obj, ctx):
            i2 = (ctx.user == obj.user)
            i1 = (not i2)
            if (not i1):
                raise Exception('Necessary Failure')
        """

        obj = FakeArgs()
	obj.user = 1
        ctx = FakeArgs()
	ctx.user = 1

        with self.assertRaises(Exception):
           policy_output_validator(obj, ctx)

    def test_bin(self):
        xproto = \
"""
    policy output < (ctx.is_admin = True | obj.empty = True) | False>
"""

        args = FakeArgs()
        args.inputs = xproto
        args.target = self.target

        output = XOSGenerator.generate(args)
        exec(output) # This loads the generated function, which should look like this:

        """
        def policy_output_validator(obj, ctx):
            i2 = (ctx.is_admin == True)
            i3 = (obj.empty == True)
            i1 = (i2 or i3)
            if (not i1):
                raise Exception('Necessary Failure')
        """

        obj = FakeArgs()
	obj.empty = False

	ctx = FakeArgs()
	ctx.is_admin = False

        with self.assertRaises(Exception):
            verdict = policy_output_validator(obj, ctx)

        
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
        def policy_output_validator(obj, ctx):
            i1 = Privilege.objects.filter(Q(object_id=obj.id))[0]
            if (not i1):
                raise Exception('Necessary Failure')
        """

        self.assertTrue(policy_output_validator is not None)
	
    def test_python(self):
        xproto = \
"""
    policy output < {{ "jack" in ["the", "box"] }} = True >
"""
	args = FakeArgs()
        args.inputs = xproto
        args.target = self.target
        output = XOSGenerator.generate(args)
        exec(output) # This loads the generated function, which should look like this:

        """
        def policy_output_validator(obj, ctx):
            i2 = ('jack' in ['the', 'box'])
            i1 = (i2 == True)
            if (not i1):
                raise Exception('Necessary Failure')
        """

        with self.assertRaises(Exception):
            self.assertTrue(policy_output_validator({}, {}) is True)

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
        def policy_sub_policy_validator(obj, ctx):
            i1 = (ctx.user == obj.user)
            if (not i1):
                raise ValidationError('Necessary Failure')

        def policy_output_validator(obj, ctx):
            i1 = policy_sub_policy_validator(obj.child, ctx)
            if (not i1):
                raise ValidationError('Necessary Failure')
        """

        obj = FakeArgs()
        obj.child = FakeArgs()
	obj.child.user = 1

        ctx = FakeArgs()
	ctx.user = 1

        with self.assertRaises(Exception):
            verdict = policy_output_enforcer(obj, ctx)

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

        self.assertIn('policy_output_validator', output)

if __name__ == '__main__':
    unittest.main()
