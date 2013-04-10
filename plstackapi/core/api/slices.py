import re
from plstackapi.openstack.client import OpenStackClient
from plstackapi.openstack.driver import OpenStackDriver
from plstackapi.core.api.auth import auth_check
from plstackapi.core.models import Slice, Site
 
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

def lookup_site(fields):
    site = None
    if 'name' in fields:
        validate_name(fields['name'])
        login_base = fields['name'][:fields['name'].find('@')]        
        sites = Site.objects.filter(login_base=login_base)
        if sites:
            site = sites[0]
    elif 'site' in fields:
        if isinstance(fields['site'], int):
            sites = Site.objects.filter(id=fields['site'])
        else:
            sites = Site.objects.filter(login_base=fields['site'])
        if sites:
            site = sites[0]     
    return site 

def add_slice(auth, fields):
    driver = OpenStackDriver(client = auth_check(auth))
    site = lookup_site(fields) 
    if site: fields['site'] = site     
    slice = Slice(**fields)
    # create tenant
    nova_fields = {'tenant_name': slice.name,
                   'description': slice.description,
                   'enabled': slice.enabled}
    tenant = driver.create_tenant(**nova_fields)
    slice.tenant_id=tenant.id
    
    # create network
    network = driver.create_network(name=self.name)
    self.network_id = network['id']

    # create router
    router = driver.create_router(name=self.name)
    self.router_id = router['id']    

    slice.save()
    return slice

def update_slice(auth, id, **fields):
    driver = OpenStackDriver(client = auth_check(auth))
    slices = Slice.objects.filter(id=id)
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
    site = lookup_site(fields)
    if site: fields['site'] = site
    slice.update(**fields)

    return slice 

def delete_slice(auth, filter={}):
    driver = OpenStackDriver(client = auth_check(auth))   
    slices = Slice.objects.filter(**filter)
    for slice in slices:
        driver.delete_slice(id=slice.tenant_id) 
        slice.delete()
    return 1

def get_slices(auth, filter={}):
    client = auth_check(auth)
    site = lookup_site(filter)
    if site: filter['site'] = site
    slices = Slice.objects.filter(**filter)
    return slices             
        

    
