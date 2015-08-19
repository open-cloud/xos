from types import StringTypes
from django.contrib.auth import authenticate
from openstack.manager import OpenStackManager
from core.models import Instance, Slice
from core.api.images import _get_images
from core.api.slices import _get_slices
from core.api.deployment_networks import _get_deployment_networks
from core.api.nodes import _get_nodes

def _get_instances(filter):
    if isinstance(filter, StringTypes) and filter.isdigit():
        filter = int(filter)
    if isinstance(filter, int):
        instances = Instance.objects.filter(id=filter)
    elif isinstance(filter, StringTypes):
        instances = Instance.objects.filter(name=filter)
    elif isinstance(filter, dict):
        instances = Instance.objects.filter(**filter)
    else:
        instances = []
    return instances
 
def add_instance(auth, fields):
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

    instance = Instance(**fields)
    auth['tenant'] = instance.slice.name
    instance.os_manager = OpenStackManager(auth=auth, caller = user)    
    instance.save()
    return instance

def update_instance(auth, instance, **fields):
    return  

def delete_instance(auth, filter={}):
    user = authenticate(username=auth.get('username'),
                        password=auth.get('password'))
    instances = _get_instances(filter)
    for instance in instances:
        auth['tenant'] = instance.slice.name 
        slice.os_manager = OpenStackManager(auth=auth, caller = user)
        instance.delete()
    return 1

def get_instances(auth, filter={}):
    user = authenticate(username=auth.get('username'),
                        password=auth.get('password'))
    if 'slice' in filter:
        slices = _get_slices(filter.get('slice'))
        if slices: filter['slice'] = slices[0]
    instances = _get_instances(filter)
    return instances             
        

    
