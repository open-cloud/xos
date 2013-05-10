from types import StringTypes
from django.contrib.auth import authenticate
from openstack.manager import OpenStackManager
from core.models import SliceMembership
from core.api.users import _get_users
from core.api.slices import _get_slices
from core.api.roles import _get_roles

def _get_slice_memberships(filter):
    if isinstance(filter, StringTypes) and filter.isdigit():
        filter = int(filter)
    if isinstance(filter, int):
        slice_memberships = SitePrivilege.objects.filter(id=filter)
    elif isinstance(filter, StringTypes):
        slice_memberships = SitePrivilege.objects.filter(name=filter)
    elif isinstance(filter, dict):
        slice_memberships = SitePrivilege.objects.filter(**filter)
    else:
        slice_memberships = []
    return slice_memberships

 
def add_slice_membership(auth, fields):
    user = authenticate(username=auth.get('username'),
                        password=auth.get('password'))

    users = _get_users(fields.get('user')) 
    slices = _get_slices(fields.get('slice')) 
    roles = _get_roles(fields.get('role'))
    
    if users: fields['user'] = users[0]     
    if slices: fields['slice'] = slices[0] 
    if roles: fields['role'] = roles[0]
 
    slice_membership = SliceMembership(**fields)
    auth['tenant'] = sites[0].login_base
    slice_membership.os_manager = OpenStackManager(auth=auth, caller = user) 
    slice_membership.save()
    return slice_membership

def update_slice_membership(auth, id, **fields):
    return  

def delete_slice_membership(auth, filter={}):
    user = authenticate(username=auth.get('username'),
                        password=auth.get('password'))
    auth['tenant'] = user.site.login_base

    slice_memberships = _get_slice_memberships(filter)
    for slice_membership in slice_memberships:
        slice_membership.os_manager = OpenStackManager(auth=auth, caller = user)
        slice_membership.delete()
    return 1

def get_slice_memberships(auth, filter={}):
    user = authenticate(username=auth.get('username'),
                        password=auth.get('password'))
    users = _get_users(fields.get('user'))
    slices = _get_slices(fields.get('slice'))
    roles = _get_roles(fields.get('role'))

    if users: fields['user'] = users[0]
    if slices: fields['slice'] = slices[0]
    if roles: fields['role'] = roles[0]

    slice_memberships = _get_slice_memberships(filter)
    return slice_memberships             
        

    
