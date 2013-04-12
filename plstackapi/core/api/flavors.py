from types import StringTypes
from plstackapi.openstack.client import OpenStackClient
from plstackapi.openstack.driver import OpenStackDriver
from plstackapi.core.api.auth import auth_check
from plstackapi.core.models import Flavor
 
def _get_flavors(filter):
    if isinstance(filter, StringTypes) and filter.isdigit():
        filter = int(filter)
    if isinstance(filter, int):
        flavors = Flavor.objects.filter(id=filter)
    elif isinstance(filter, StringTypes):
        flavors = Flavor.objects.filter(name=filter)
    elif isinstance(filter, dict):
        flavors = Flavor.objects.filter(**filter)
    else:
        flavors = []
    return flavors

def add_flavor(auth, fields={}):
    """not implemented"""
    return 

def delete_flavor(auth, filter={}):
    """not implemented"""
    return 1

def get_flavors(auth, filter={}):
    auth_check(auth)   
    flavors = _get_flavors(filter)
    return flavors             
        

    
