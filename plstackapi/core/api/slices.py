import re
from types import StringTypes
from plstackapi.openstack.client import OpenStackClient
from plstackapi.openstack.driver import OpenStackDriver
from plstackapi.core.api.auth import auth_check
from plstackapi.core.models import Slice
from plstackapi.core.api.sites import _get_sites

def validate_name(name):
    # N.B.: Responsibility of the caller to ensure that login_base
        # portion of the slice name corresponds to a valid site, if
        # desired.

        # 1. Lowercase.
        # 2. Begins with login_base (letters or numbers).
        # 3. Then single underscore after login_base.
        # 4. Then letters, numbers, or underscores.
        good_name = r'^[a-z0-9]+_[a-zA-Z0-9_]+$'
        if not name or \
           not re.match(good_name, name):
            raise Exception, "Invalid slice name: %s" % name

def _get_slices(filter):
    if isinstance(filter, StringTypes) and filter.isdigit():
        filter = int(filter)
    if isinstance(filter, int):
        slices = Slice.objects.filter(id=filter)
    elif isinstance(filter, StringTypes):
        slices = Slice.objects.filter(name=filter)
    elif isinstance(filter, dict):
        slices = Slice.objects.filter(**filter)
    else:
        slices = []
    return slices
    
 
def add_slice(auth, fields):
    driver = OpenStackDriver(client = auth_check(auth))
    validate_name(fields.get('name'))
    login_base = fields['name'][:fields['name'].find('_')]
    sites = _get_sites(login_base) 
    if sites: fields['site'] = sites[0]     
    slice = Slice(**fields)
   
    # create tenant
    nova_fields = {'tenant_name': slice.name,
                   'description': slice.description,
                   'enabled': slice.enabled}
    tenant = driver.create_tenant(**nova_fields)
    slice.tenant_id=tenant.id
    
    # create network
    network = driver.create_network(slice.name)
    slice.network_id = network['id']

    # create router
    router = driver.create_router(slice.name)
    slice.router_id = router['id']    

    slice.save()
    return slice

def update_slice(auth, id, **fields):
    driver = OpenStackDriver(client = auth_check(auth))
    slices = _get_slices(id)
    if not slices:
        return

    # update tenant
    slice = slices[0]
    nova_fields = {}
    if 'name' in fields:
        nova_fields['tenant_name'] = fields['name']
    if 'description' in fields:
        nova_fields['description'] = fields['description']
    if 'enabled' in fields:
        nova_fields['enabled'] = fields['enabled']
    driver.update_tenant(slice.tenant_id, **nova_fields)

    # update db record 
    sites = _get_sites(fields.get('site'))
    if sites: fields['site'] = sites[0]
    slice.update(**fields)

    return slice 

def delete_slice(auth, filter={}):
    driver = OpenStackDriver(client = auth_check(auth))   
    slices = _get_slices(id)
    for slice in slices:
        driver.delete_slice(id=slice.tenant_id) 
        slice.delete()
    return 1

def get_slices(auth, filter={}):
    client = auth_check(auth)
    if 'site' in filter:
        sites = _get_sites(filter.get('site'))
        if sites: filter['site'] = sites[0]
    slices = _get_slices(filter)
    return slices             
        

    
