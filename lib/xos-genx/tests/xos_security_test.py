
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
import mock

"""The function below is for eliminating warnings arising due to the missing policy_output_enforcer,
which is generated and loaded dynamically.
"""
def policy_output_enforcer(x, y):
    raise Exception("Security enforcer not generated. Test failed.")
    return False

"""
The tests below use the Python code target to generate 
Python security policies, set up an appropriate environment and execute the Python.
The security policies here deliberately made complex in order to stress the processor.
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
    policy test_policy < ctx.user.is_admin | exists Privilege: Privilege.accessor_id = ctx.user.id & Privilege.object_type = "Deployment" & Privilege.permission = "role:admin" & Privilege.object_id = obj.id >
"""
        args = FakeArgs()
        args.inputs = xproto
        args.target = self.target

        output = XOSGenerator.generate(args)

        exec(output) # This loads the generated function, which should look like this:

        """
        def policy_output_enforcer(obj, ctx):
            i2 = ctx.user.is_admin
            i3 = Privilege.objects.filter(Q(accessor_id=ctx.user.id), Q(object_type='Deployment'), Q(permission='role:admin'), Q(object_id=obj.id))[0]
            i1 = (i2 or i3)
                return i1
        """

        # FIXME: Test this policy by executing it
        self.assertTrue(policy_output_enforcer is not None)

    """
    This is the security policy for ControllerNetworks
    """
    def test_controller_network_policy(self):
        xproto = \
"""
    policy test_policy < 
         ctx.user.is_admin
         | (exists Privilege:
             Privilege.accessor_id = ctx.user.id
             & Privilege.accessor_type = "User"
             & Privilege.object_type = "Slice"
             & Privilege.object_id = obj.owner.id)
         | (exists Privilege:
             Privilege.accessor_id = ctx.user.id
             & Privilege.accessor_type = "User"
             & Privilege.object_type = "Site"
             & Privilege.object_id = obj.owner.site.id
             & Privilege.permission = "role:admin") >
"""
        args = FakeArgs()
        args.inputs = xproto
        args.target = self.target

        output = XOSGenerator.generate(args)
        exec(output) # This loads the generated function, which should look like this:

        """
        def policy_output_enforcer(obj, ctx):
            i2 = ctx.user.is_admin
            i4 = Privilege.objects.filter(Q(accessor_id=ctx.user.id), Q(accessor_type='User'), Q(object_type='Slice'), Q(object_id=obj.owner.id))[0]
            i5 = Privilege.objects.filter(Q(accessor_id=ctx.user.id), Q(accessor_type='User'), Q(object_type='Site'), Q(object_id=obj.owner.site.id), Q(permission='role:admin'))[0]
            i3 = (i4 or i5)
            i1 = (i2 or i3)
            return i1
        """

        # FIXME: Test this policy by executing it
        self.assertTrue(policy_output_enforcer is not None)

    """
    This is the security policy for Slices
    """
    def test_slice_policy(self):
        xproto = \
"""
   policy site_policy <
            ctx.user.is_admin
            | (ctx.write_access -> exists Privilege: Privilege.object_type = "Site" & Privilege.object_id = obj.id & Privilege.accessor_id = ctx.user.id & Privilege.permission_id = "role:admin") >

   policy test_policy <
         ctx.user.is_admin
         | (*site_policy(site)
         & ((exists Privilege:
             Privilege.accessor_id = ctx.user.id
             & Privilege.accessor_type = "User"
             & Privilege.object_type = "Slice"
             & Privilege.object_id = obj.id
             & (ctx.write_access->Privilege.permission="role:admin"))
           | (exists Privilege:
             Privilege.accessor_id = ctx.user.id
             & Privilege.accessor_type = "User"
             & Privilege.object_type = "Site"
             & Privilege.object_id = obj.site.id
             & Privilege.permission = "role:admin"))
            )>
    
"""
        args = FakeArgs()
        args.inputs = xproto
        args.target = self.target

        output = XOSGenerator.generate(args)

        exec(output) # This loads the generated function, which should look like this:

        """
        def policy_output_enforcer(obj, ctx):
	    i2 = ctx.user.is_admin
	    i4 = policy_site_policy_enforcer(obj.site, ctx)
	    i10 = ctx.write_access
	    i11 = (not (not Privilege.objects.filter(Q(accessor_id=ctx.user.id), Q(accessor_type='User'), Q(object_type='Slice'), Q(object_id=obj.id), Q(permission='role:admin'))))
	    i8 = (i10 and i11)
	    i14 = ctx.write_access
	    i12 = (not i14)
	    i13 = (not (not Privilege.objects.filter(Q(accessor_id=ctx.user.id), Q(accessor_type='User'), Q(object_type='Slice'), Q(object_id=obj.id))))
	    i9 = (i12 and i13)
	    i6 = (i8 or i9)
	    i7 = (not (not Privilege.objects.filter(Q(accessor_id=ctx.user.id), Q(accessor_type='User'), Q(object_type='Site'), Q(object_id=obj.site.id), Q(permission='role:admin'))))
	    i5 = (i6 or i7)
	    i3 = (i4 and i5)
	    i1 = (i2 or i3)
	    return i1
        """

        # FIXME: Test this policy by executing it
        self.assertTrue(policy_output_enforcer is not None)

    """
    This is the security policy for Users
    """
    def test_user_policy(self):
        xproto = \
"""
    policy test_policy <
         ctx.user.is_admin
         | ctx.user.id = obj.id
         | (exists Privilege: 
             Privilege.accessor_id = ctx.user.id
             & Privilege.accessor_type = "User"
             & Privilege.permission = "role:admin"
             & Privilege.object_type = "Site"
             & Privilege.object_id = ctx.user.site.id) >
"""
        args = FakeArgs()
        args.inputs = xproto
        args.target = self.target

        output = XOSGenerator.generate(args)

        exec(output) # This loads the generated function, which should look like this:

        """
        def policy_output_enforcer(obj, ctx):
            i2 = ctx.user.is_admin
            i4 = (ctx.user.id == obj.id)
            i5 = Privilege.objects.filter(Q(accessor_id=ctx.user.id), Q(accessor_type='User'), Q(permission='role:admin'), Q(object_type='Site'), Q(object_id=ctx.user.site.id))[0]
            i3 = (i4 or i5)
            i1 = (i2 or i3)
            return i1
        """

        # FIXME: Test this policy by executing it
        self.assertTrue(policy_output_enforcer is not None)

if __name__ == '__main__':
    unittest.main()
