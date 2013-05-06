from types import StringTypes
from django.contrib.auth import authenticate
from plstackapi.core.models import Image
 
def _get_images(filter):
    if isinstance(filter, StringTypes) and filter.isdigit():
        filter = int(filter)
    if isinstance(filter, int):
        images = Image.objects.filter(id=filter)
    elif isinstance(filter, StringTypes):
        images = Image.objects.filter(name=filter)
    elif isinstance(filter, dict):
        images = Image.objects.filter(**filter)
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
    user = authenticate(username=auth.get('username'),
                        password=auth.get('password'))
    images = _get_images(filter)
    return images             
        

    
