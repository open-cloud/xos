from plstackapi.openstack.client import OpenStackClient
from plstackapi.openstack.driver import OpenStackDriver
from plstackapi.planetstack.api.auth import auth_check
from plstackapi.planetstack.models import *
 

def add_role(auth, name):
    client = auth_check(auth)
    keystone_role = client.keystone.roles.create(name)
    role = Role(role_type=name, role_id=keystone_role.id)
    role.save()
    return role

def delete_role(auth, name):
    client = auth_check(auth)
    role = Role.objects.filter(role_type=name)
    client.keystone.roles.delete(role.role_id)
    role.delete()
    return 1

def get_roles(auth, filter={}):
    client = auth_check(auth)
    roles = Role.objects.filter(**filter)
    return roles             
        

    
