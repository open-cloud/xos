from types import StringTypes
from plstackapi.openstack.client import OpenStackClient
from plstackapi.openstack.driver import OpenStackDriver
from plstackapi.core.api.auth import auth_check
from plstackapi.core.models import User, Site
from plstackapi.core.api.sites import _get_sites

def _get_users(filter):
    if isinstance(filter, StringTypes) and filter.isdigit():
        filter = int(filter)
    if isinstance(filter, int):
        users = User.objects.filter(id=filter)
    elif isinstance(filter, StringTypes):
        users = User.objects.filter(email=filter)
    elif isinstance(filter, dict):
        users = User.objects.filter(**filter)
    else:
        users = []
    return users 

def add_user(auth, fields):
    driver = OpenStackDriver(client = auth_check(auth))
    sites = _get_sites(fields.get('site')) 
    if sites: fields['site'] = sites[0]     
    user = User(**fields)
    nova_fields = {'name': user.email[:user.email.find('@')],
                   'email': user.email, 
                   'password': fields.get('password'),
                   'enabled': user.enabled}    
    nova_user = driver.create_user(**nova_fields)
    #driver.add_user_user(user.id, user.site.tenant_id, 'user')
    user.user_id=nova_user.id
    user.save()
    return user

def update_user(auth, id, **fields):
    driver = OpenStackDriver(client = auth_check(auth))
    users = User.objects.filter(id=id)
    if not users:
        return

    user = users[0]
    nova_fields = {}
    if 'email' in fields:
        nova_fields['name'] = fields['email'][:self.email.find('@')]
        nova_fields['email'] = fields['email']
    if 'password' in fields:
        nova_fields['password'] = fields['password']
    if 'enabled' in fields:
        nova_fields['enabled'] = fields['enabled']
    driver.update_user(user.user_id, **nova_fields)
    sites = _get_sites(fields.get('site'))
    if sites: fields['site'] = sites[0]
    user.update(**fields)
    return user 

def delete_user(auth, filter={}):
    driver = OpenStackDriver(client = auth_check(auth))   
    users = _get_users(filter)
    for user in users:
        driver.delete_user(id=user.user_id) 
        user.delete()
    return 1

def get_users(auth, filter={}):
    client = auth_check(auth)
    users = _get_users(filter)
    return users             
        

    
