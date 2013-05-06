from types import StringTypes
from django.contrib.auth import authenticate
from plstackapi.openstack.manager import OpenStackManager    
from plstackapi.core.api.auth import auth_check
from plstackapi.core.models import Site


def _get_sites(filter):
    if isinstance(filter, StringTypes) and filter.isdigit():
        filter = int(filter)
    if isinstance(filter, int):
        sites = Site.objects.filter(id=filter)
    elif isinstance(filter, StringTypes):
        sites = Site.objects.filter(login_base=filter)
    elif isinstance(filter, dict):
        sites = Site.objects.filter(**filter)
    else:
        sites = []
    return sites 

def add_site(auth, fields):
    user = authenticate(username=auth.get('username'),
                        password=auth.get('password'))
    auth['tenant'] = user.site.login_base

    site = Site(**fields)
    site.os_manager = OpenStackManager(auth=auth, caller = user)
    site.save()
    return site

def update_site(auth, id, **fields):
    user = authenticate(username=auth.get('username'),
                        password=auth.get('password'))
    auth['tenant'] = user.site.login_base

    sites = _get_sites(id)
    if not sites:
        return

    site = Site[0]
    site.os_manager = OpenStackManager(auth=auth, caller = user)
    site.update(**fields)
    return site 

def delete_site(auth, filter={}):
    user = authenticate(username=auth.get('username'),
                        password=auth.get('password'))
    auth['tenant'] = user.site.login_base
    sites = _get_sites(id)
    for site in sites:
        site.os_manager = OpenStackManager(auth=auth, caller = user)
        site.delete()
    return 1

def get_sites(auth, filter={}):
    user = authenticate(username=auth.get('username'),
                        password=auth.get('password'))
    sites = _get_sites(filter)
    return sites             
        

    
