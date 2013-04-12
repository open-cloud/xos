from types import StringTypes
from plstackapi.openstack.client import OpenStackClient
from plstackapi.openstack.driver import OpenStackDriver
from plstackapi.core.api.auth import auth_check
from plstackapi.core.models import SliceMembership, Slice, Role, User
from plstackapi.core.api.users import _get_users
from plstackapi.core.api.slices import _get_slices
from plstackapi.core.api.roles import _get_roles

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
    driver = OpenStackDriver(client = auth_check(auth))
    users = _get_users(fields.get('user')) 
    slices = _get_slices(fields.get('slice')) 
    roles = _get_roles(fields.get('role'))
    
    if users: fields['user'] = users[0]     
    if slices: fields['slice'] = slices[0] 
    if roles: fields['role'] = roles[0]
 
    slice_membership = SliceMembership(**fields)

    # update nova role
    driver.add_user_role(slice_membership.user.user_id, 
                         slice_membership.slice.tenant_id, 
                         slice_membership.role.name)
    
    slice_membership.save()
    return slice_membership

def update_slice_membership(auth, id, **fields):
    return  

def delete_slice_membership(auth, filter={}):
    driver = OpenStackDriver(client = auth_check(auth))   
    slice_memberships = _get_slice_memberships(filter)
    for slice_membership in slice_memberships:
        driver.delete_user_role(user_id=slice_membership.user.id,
                                tenant_id = slice_membership.slice.tenant_id,
                                role_name = slice_membership.role.name) 
        slice_membership.delete()
    return 1

def get_slice_memberships(auth, filter={}):
    client = auth_check(auth)
    users = _get_users(fields.get('user'))
    slices = _get_slices(fields.get('slice'))
    roles = _get_roles(fields.get('role'))

    if users: fields['user'] = users[0]
    if slices: fields['slice'] = slices[0]
    if roles: fields['role'] = roles[0]

    slice_memberships = _get_slice_memberships(filter)
    return slice_memberships             
        

    
