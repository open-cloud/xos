from plstackapi.openstack.client import OpenStackClient
from plstackapi.openstack.driver import OpenStackDriver
from plstackapi.core.api.auth import auth_check
from plstackapi.core.models import Image
 
def _get_images(filter):
    if isinstance(filter, int):
        images = image.objects.filter(id=filter)
    elif isinstance(filter, StringTypes):
        images = image.objects.filter(name=filter)
    elif isinstance(filer, dict):
        images = image.objects.filter(**filter)
    else:
        images = []
    return images

def add_image(auth, fields={}):
    """not implemented"""
    return 

def delete_image(auth, filter={}):
    """not implemented"""
    return 1

def get_images(auth, filter={}):
    auth_check(auth)   
    images = _get_images(filter)
    return images             
        

    
