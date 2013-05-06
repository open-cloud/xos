from types import StringTypes
from django.contrib.auth import authenticate
from plstackapi.openstack.manager import OpenStackManager    
from plstackapi.core.models import PLUser, Site
from plstackapi.core.api.sites import _get_sites

def _get_users(filter):
    if isinstance(filter, StringTypes) and filter.isdigit():
        filter = int(filter)
    if isinstance(filter, int):
        users = PLUser.objects.filter(id=filter)
    elif isinstance(filter, StringTypes):
        users = PLUser.objects.filter(email=filter)
    elif isinstance(filter, dict):
        users = PLUser.objects.filter(**filter)
    else:
        users = []
    return users 

def add_user(auth, fields):
    user = authenticate(username=auth.get('username'),
                        password=auth.get('password'))
    auth['tenant'] = user.site.login_base

    sites = _get_sites(fields.get('site')) 
    if sites: fields['site'] = sites[0]     
    user = PLUser(**fields)
    user.os_manager = OpenStackManager(auth=auth, caller = user)
    user.save()
    return user

def update_user(auth, id, **fields):
    user = authenticate(username=auth.get('username'),
                        password=auth.get('password'))
    auth['tenant'] = user.site.login_base

    users = PLUser.objects.filter(id=id)
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

    
    sites = _get_sites(fields.get('site'))
    if sites: fields['site'] = sites[0]
    user.os_manager = OpenStackManager(auth=auth, caller = user)
    for (k,v) in fields.items():
        setattr(user, k, v)    
    user.save()
    return user 

def delete_user(auth, filter={}):
    user = authenticate(username=auth.get('username'),
                        password=auth.get('password'))
    auth['tenant'] = user.site.login_base
    users = _get_users(filter)
    for user in users:
        user.os_manager = OpenStackManager(auth=auth, caller = user) 
        user.delete()
    return 1

def get_users(auth, filter={}):
    user = authenticate(username=auth.get('username'),
                        password=auth.get('password'))
    users = _get_users(filter)
    return users             
        

    
