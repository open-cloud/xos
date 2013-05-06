from types import StringTypes
from django.contrib.auth import authenticate
from plstackapi.openstack.manager import OpenStackManager
from plstackapi.core.models import Role
 

def _get_roles(filter):
    if isinstance(filter, StringTypes) and filter.isdigit():
        filter = int(filter)
    if isinstance(filter, int):
        roles = Role.objects.filter(id=filter)
    elif isinstance(filter, StringTypes):
        roles = Role.objects.filter(role_type=filter)
    elif isinstance(filter, dict):
        roles = Role.objects.filter(**filter)
    else:
        roles = []
    return roles

def add_role(auth, name):
    user = authenticate(username=auth.get('username'),
                        password=auth.get('password'))
    auth['tenant'] = user.site.login_base

    role = Role(role_type=name)
    role.os_manager = OpenStackManager(auth=auth, caller = user) 
    role.save()
    return role

def delete_role(auth, filter={}):
    user = authenticate(username=auth.get('username'),
                        password=auth.get('password'))
    roles = _get_roles(filter) 
    for role in roles:
        auth['tenant'] = user.site.login_base
        role.os_manager = OpenStackManager(auth=auth, caller = user)
        role.delete()
    return 1

def get_roles(auth, filter={}):
    user = authenticate(username=auth.get('username'),
                        password=auth.get('password'))
    return _get_roles(filter)             
        
