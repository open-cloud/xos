import re
from types import StringTypes
from django.contrib.auth import authenticate
from openstack.manager import OpenStackManager
from core.models import Slice
from core.api.sites import _get_sites

def _get_slices(filter):
    if isinstance(filter, StringTypes) and filter.isdigit():
        filter = int(filter)
    if isinstance(filter, int):
        slices = Slice.objects.filter(id=filter)
    elif isinstance(filter, StringTypes):
        slices = Slice.objects.filter(name=filter)
    elif isinstance(filter, dict):
        slices = Slice.objects.filter(**filter)
    else:
        slices = []
    return slices
    
 
def add_slice(auth, fields):
    user = authenticate(username=auth.get('username'),
                        password=auth.get('password'))
    auth['tenant'] = user.site.login_base

    login_base = fields['name'][:fields['name'].find('_')]
    sites = _get_sites(login_base) 
    if sites: fields['site'] = sites[0]     
    slice = Slice(**fields)
    slice.os_manager = OpenStackManager(auth=auth, caller = user) 
    slice.save()
    return slice

def update_slice(auth, id, **fields):
    user = authenticate(username=auth.get('username'),
                        password=auth.get('password'))
    auth['tenant'] = user.site.login_base

    slices = _get_slices(id)
    if not slices:
        return
    slice = slices[0]
    sites = _get_sites(fields.get('site'))
    if sites: fields['site'] = sites[0]

    slice.os_manager = OpenStackManager(auth=auth, caller = user)
    for (k,v) in fields.items():
        setattr(slice, k, v)
    slice.save()

    return slice 

def delete_slice(auth, filter={}):
    user = authenticate(username=auth.get('username'),
                        password=auth.get('password'))
    auth['tenant'] = user.site.login_base
    slices = _get_slices(filter)
    for slice in slices:
        slice.os_manager = OpenStackManager(auth=auth, caller = user) 
        slice.delete()
    return 1

def get_slices(auth, filter={}):
    user = authenticate(username=auth.get('username'),
                        password=auth.get('password'))
    if 'site' in filter:
        sites = _get_sites(filter.get('site'))
        if sites: filter['site'] = sites[0]
    slices = _get_slices(filter)
    return slices             
        

    
