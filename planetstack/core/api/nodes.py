from types import StringTypes
from openstack.client import OpenStackClient
from openstack.driver import OpenStackDriver
from core.api.auth import auth_check
from core.models import Node
 
def _get_nodes(filter):
    if isinstance(filter, StringTypes) and filter.isdigit():
        filter = int(filter)
    if isinstance(filter, int):
        nodes = Node.objects.filter(id=filter)
    elif isinstance(filter, StringTypes):
        nodes = Node.objects.filter(name=filter)
    elif isinstance(filter, dict):
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
        

    
