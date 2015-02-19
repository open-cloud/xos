from types import StringTypes
from django.contrib.auth import authenticate
from openstack.manager import OpenStackManager
from core.models import Sliver, Slice
from core.api.images import _get_images
from core.api.slices import _get_slices
from core.api.deployment_networks import _get_deployment_networks
from core.api.nodes import _get_nodes

def _get_slivers(filter):
    if isinstance(filter, StringTypes) and filter.isdigit():
        filter = int(filter)
    if isinstance(filter, int):
        slivers = Sliver.objects.filter(id=filter)
    elif isinstance(filter, StringTypes):
        slivers = Sliver.objects.filter(name=filter)
    elif isinstance(filter, dict):
        slivers = Sliver.objects.filter(**filter)
    else:
        slivers = []
    return slivers
 
def add_sliver(auth, fields):
    user = authenticate(username=auth.get('username'),
                        password=auth.get('password'))
    
    images = _get_images(fields.get('image'))
    slices = _get_slices(fields.get('slice'))
    deployment_networks = _get_deployment_networks(fields.get('deploymentNetwork'))
    nodes = _get_nodes(fields.get('node'))
    if images: fields['image'] = images[0]     
    if slices: fields['slice'] = slices[0]     
    if deployment_networks: fields['deploymentNetwork'] = deployment_networks[0]     
    if nodes: fields['node'] = nodes[0]     

    sliver = Sliver(**fields)
    auth['tenant'] = sliver.slice.name
    sliver.os_manager = OpenStackManager(auth=auth, caller = user)    
    sliver.save()
    return sliver

def update_sliver(auth, sliver, **fields):
    return  

def delete_sliver(auth, filter={}):
    user = authenticate(username=auth.get('username'),
                        password=auth.get('password'))
    slivers = _get_slivers(filter)
    for sliver in slivers:
        auth['tenant'] = sliver.slice.name 
        slice.os_manager = OpenStackManager(auth=auth, caller = user)
        sliver.delete()
    return 1

def get_slivers(auth, filter={}):
    user = authenticate(username=auth.get('username'),
                        password=auth.get('password'))
    if 'slice' in filter:
        slices = _get_slices(filter.get('slice'))
        if slices: filter['slice'] = slices[0]
    slivers = _get_slivers(filter)
    return slivers             
        

    
