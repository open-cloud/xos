from plstackapi.openstack.client import OpenStackClient
from plstackapi.openstack.driver import OpenStackDriver
from plstackapi.core.api.auth import auth_check
from plstackapi.core.models import Flavor
 

def add_flavor(auth, fields={}):
    """not implemented"""
    return 

def delete_flavor(auth, filter={}):
    """not implemented"""
    return 1

def get_flavors(auth, filter={}):
    auth_check(auth)   
    flavors = Flavor.objects.filter(**filter)
    return flavors             
        

    
