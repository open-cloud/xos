
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
class XProtoXOSModelValidationTest(unittest.TestCase):
    def setUp(self):
        self.target = XProtoTestHelpers.write_tmp_target("{{ xproto_fol_to_python_validator('output', proto.policies.test_policy, None, 'Necessary Failure') }}")

    def test_instance_container(self):
        xproto = \
"""
    policy test_policy < (obj.isolation = "container" | obj.isolation = "container_vm" ) -> (obj.image.kind = "container") >
"""
        args = FakeArgs()
        args.inputs = xproto
        args.target = self.target

        output = XOSGenerator.generate(args)

        obj = FakeArgs()
        obj.isolation = 'container'
        obj.kind = 'not a container'

        exec(output) # This loads the generated function, which should look like this:

        """
        def policy_output_validator(obj, ctx):
            i4 = (obj.isolation == 'container')
            i5 = (self.isolation == 'container_vm')
            i2 = (i4 or i5)
            i3 = (obj.image.kind == 'container')
            i1 = (i2 or i3)
            return i1
        """

        with self.assertRaises(Exception):
           policy_output_validator(obj, {})
    
    def test_slice_name_validation(self):
        xproto = \
"""
    policy test_policy < not obj.id -> {{ obj.name.startswith(obj.site.login_base) }} >
"""
        args = FakeArgs()
        args.inputs = xproto
        args.target = self.target

        output = XOSGenerator.generate(args)

        obj = FakeArgs()
        obj.isolation = 'container'
        obj.kind = 'not a container'

        exec(output) # This loads the generated function, which should look like this:

        """
        def policy_output_validator(obj, ctx):
            i3 = obj.id
            i4 = obj.name.startswith(obj.site.login_base)
            i2 = ((not i3) or i4)
            i1 = (not i2)
            if (not i1):
                raise ValidationError('Necessary Failure')
        """

        with self.assertRaises(Exception):
           policy_output_validator(obj, {})

    def test_equal(self):
        xproto = \
"""
    policy test_policy < not (ctx.user = obj.user) >
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
    policy test_policy < not (ctx.is_admin = True | obj.empty = True) | False>
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
	obj.empty = True

	ctx = FakeArgs()
	ctx.is_admin = True

        with self.assertRaises(Exception):
            verdict = policy_output_validator(obj, ctx)

        
    def test_exists(self):
        xproto = \
"""
    policy test_policy < exists Privilege: Privilege.object_id = obj.id >
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
    policy test_policy < {{ "jack" in ["the", "box"] }} = True >
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

    def test_forall(self):
        # This one we only parse
        xproto = \
"""
    policy test_policy < forall Credential: Credential.obj_id = obj_id >
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
