from plstackapi.openstack.client import OpenStackClient
from plstackapi.openstack.driver import OpenStackDriver
from plstackapi.planetstack.api.auth import auth_check
from plstackapi.planetstack.models import Image
 

def add_image(auth, fields={}):
    """not implemented"""
    return 

def delete_image(auth, filter={}):
    """not implemented"""
    return 1

def get_images(auth, filter={}):
    auth_check(auth)   
    images = Image.objects.filter(**filter)
    return images             
        

    
