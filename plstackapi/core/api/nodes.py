from plstackapi.openstack.client import OpenStackClient
from plstackapi.openstack.driver import OpenStackDriver
from plstackapi.core.api.auth import auth_check
from plstackapi.core.models import Node
 
def _get_nodes(filter):
    if isinstance(filter, int):
        nodes = Node.objects.filter(id=filter)
    elif isinstance(filter, StringTypes):
        nodes = Node.objects.filter(name=filter)
    elif isinstance(filer, dict):
        nodes = Node.objects.filter(**filter)
    else:
        nodes = []
    return nodes

def add_node(auth, fields={}):
    """not implemented"""
    return 

def delete_node(auth, filter={}):
    """not implemented"""
    return 1

def update_node(auth, id, fields={}):
    return 

def get_nodes(auth, filter={}):
    auth_check(auth)   
    nodes = _get_nodes(filter)
    return nodes             
        

    
