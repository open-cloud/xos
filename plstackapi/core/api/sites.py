from plstackapi.openstack.client import OpenStackClient
from plstackapi.openstack.driver import OpenStackDriver
from plstackapi.core.api.auth import auth_check
from plstackapi.core.models import Site
 

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
    sites = Site.objects.filter(id=id)
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
    sites = Site.objects.filter(**filter)
    for site in sites:
        driver.delete_tenant(id=site.tenant_id) 
        site.delete()
    return 1

def get_sites(auth, filter={}):
    client = auth_check(auth)
    sites = Site.objects.filter(**filter)
    return sites             
        

    
