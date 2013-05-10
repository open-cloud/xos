from types import StringTypes
from openstack.client import OpenStackClient
from openstack.driver import OpenStackDriver
from core.api.auth import auth_check
from core.models import Site


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
    driver = OpenStackDriver(client = auth_check(auth))
    site = Site(**fields)
    nova_fields = {'tenant_name': site.login_base,
                   'description': site.name,
                   'enabled': site.enabled}    
    tenant = driver.create_tenant(**nova_fields)
    site.tenant_id=tenant.id
    site.save()
    return site

def update_site(auth, id, **fields):
    driver = OpenStackDriver(client = auth_check(auth))
    sites = _get_sites(id)
    if not sites:
        return

    site = Site[0]
    nova_fields = {}
    if 'description' in fields:
        nova_fields['description'] = fields['name']
    if 'enabled' in fields:
        nova_fields['enabled'] = fields['enabled']
    driver.update_tenant(site.tenant_id, **nova_fields)
    site.update(**fields)
    return site 

def delete_site(auth, filter={}):
    driver = OpenStackDriver(client = auth_check(auth))   
    sites = _get_sites(id)
    for site in sites:
        driver.delete_tenant(id=site.tenant_id) 
        site.delete()
    return 1

def get_sites(auth, filter={}):
    client = auth_check(auth)
    sites = _get_sites(filter)
    return sites             
        

    
