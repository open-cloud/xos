import commands
from types import StringTypes
from django.contrib.auth import authenticate
from plstackapi.openstack.manager import OpenStackManager
from plstackapi.core.models import Subnet
from plstackapi.core.api.slices import _get_slices


def _get_subnets(filter):
    if isinstance(filter, StringTypes) and filter.isdigit():
        filter = int(filter)
    if isinstance(filter, int):
        subnets = Subnet.objects.filter(id=filter)
    elif isinstance(filter, StringTypes):
        # the name is the subnet's slice's name
        slices = _get_slices(filter)
        slice = None
        if slices: slice=slices[0]
        subnets = Subnet.objects.filter(slice=slice)
    elif isinstance(filter, dict):
        subnets = Subnet.objects.filter(**filter)
    else:
        subnets = []
    return subnets

def add_subnet(auth, fields):
    user = authenticate(username=auth.get('username'),
                        password=auth.get('password'))
    
    slices = _get_slices(fields.get('slice')) 
    if slices: fields['slice'] = slices[0]     
    subnet = Subnet(**fields)
    auth['tenant'] = subnet.slice.name
    subnet.os_manager = OpenStackManager(auth=auth, caller = user)
    subnet.save()
    return subnet

def update_subnet(auth, subnet, **fields):
    return  

def delete_subnet(auth, filter={}):
    user = authenticate(username=auth.get('username'),
                        password=auth.get('password'))
    subnets = Subnet.objects.filter(**filter)
    for subnet in subnets:
        auth['tenant'] = subnet.slice.name
        subnet.os_manager = OpenStackManager(auth=auth, caller = user)
        subnet.delete()
    return 1

def get_subnets(auth, filter={}):
    user = authenticate(username=auth.get('username'),
                        password=auth.get('password'))
    if 'slice' in filter:
        slice = _get_slice(filter.get('slice'))
        if slice: filter['slice'] = slice
    subnets = Subnet.objects.filter(**filter)
    return subnets             
        

    
