from types import StringTypes
from django.contrib.auth import authenticate
from plstackapi.openstack.manager import OpenStackManager
from plstackapi.core.models import Key
from plstackapi.core.api.users import _get_users


def _get_keys(filter):
    if isinstance(filter, StringTypes) and filter.isdigit():
        filter = int(filter)
    if isinstance(filter, int):
        keys = Key.objects.filter(id=filter)
    elif isinstance(filter, StringTypes):
        keys = Key.objects.filter(name=filter)
    elif isinstance(filter, dict):
        keys = Key.objects.filter(**filter)
    else:
        keys = []
    return keys 

def add_key(auth, fields):
    user = authenticate(username=auth.get('username'),
                        password=auth.get('password'))
    auth['tenant'] = user.site.login_base
    manager = OpenStackManager(auth=auth, caller = user)

    # look up user object
    users = _get_users(fields.get('user')) 
    if users: fields['user'] = users[0]    
    # save
    key = Key(**fields)
    key.os_manager = manager
    key.save()
    return key

def update_key(auth, id, **fields):
    return  

def delete_key(auth, filter={}):
    user = authenticate(username=auth.get('username'),
                        password=auth.get('password'))
    auth['tenant'] = user.site.login_base
    manager = OpenStackManager(auth=auth, caller = user)

    keys = _get_keys(filter)
    for key in keys:
        key.os_manager = manager
        key.delete()
    return 1

def get_keys(auth, filter={}):
    user = authenticate(username=auth.get('username'),
                        password=auth.get('password'))
    keys = _get_keys(filter)
    return keys             
        

    
