from types import StringTypes
from plstackapi.openstack.client import OpenStackClient
from plstackapi.openstack.driver import OpenStackDriver
from plstackapi.core.api.auth import auth_check
from plstackapi.core.models import Role
 

def _get_roles(filter):
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
    driver = OpenStackDriver(client = auth_check(auth))    
    keystone_role = driver.create_role(name=name)
    role = Role(role_type=name, role_id=keystone_role.id)
    role.save()
    return role

def delete_role(auth, filter={}):
    driver = OpenStackDriver(client = auth_check(auth))   
    roles = _get_roles(filter) 
    for role in roles:
        driver.delete_role({'id': role.role_id}) 
        role.delete()
    return 1

def get_roles(auth, filter={}):
    client = auth_check(auth)
    return _get_roles(filter)             
        
