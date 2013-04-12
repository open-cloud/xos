from types import StringTypes
from plstackapi.openstack.client import OpenStackClient
from plstackapi.openstack.driver import OpenStackDriver
from plstackapi.core.api.auth import auth_check
from plstackapi.core.models import Subnet
from plstackapi.core.api.slices import _get_slices

def _get_subnets(filter):
    if isinstance(filter, StringTypes) and filter.isdigit():
        filter = int(filter)
    if isinstance(filter, int):
        subnets = Subnet.objects.filter(id=filter)
    elif isinstance(filter, StringTypes):
        subnets = Subnet.objects.filter(name=filter)
    elif isinstance(filter, dict):
        subnets = Subnet.objects.filter(**filter)
    else:
        subnets = []
    return subnets

def add_subnet(auth, fields):
    driver = OpenStackDriver(client = auth_check(auth))
    slices = _get_slice(fields.get('slice')) 
    if slices: fields['slice'] = slices[0]     
    subnet = Subnet(**fields)
    # create quantum subnet
    subnet = driver.create_subnet(network_name=subnet.name,
                                  cidr_ip = subnet.cidr,
                                  ip_version=subnet.ip_version,
                                  start = subnet.start,
                                  end = subnet.end,
                                  dns_nameservers = ['8.8.8.8', '8.8.4.4'])

    subnet.subnet_id=subnet.id

    # add subnet as interface to slice's router
    driver.add_router_interface(subnet.slice.router_id, subnet.subnet_id)     
    
    subnet.save()
    return subnet

def update_subnet(auth, subnet, **fields):
    return  

def delete_subnet(auth, filter={}):
    driver = OpenStackDriver(client = auth_check(auth))   
    subnets = Subnet.objects.filter(**filter)
    for subnet in subnets:
        driver.delete_router_interface(subnet.slice.router_id, subnet.subnet_id)
        driver.delete_subnet(subnet.subnet_id) 
        subnet.delete()
    return 1

def get_subnets(auth, filter={}):
    client = auth_check(auth)
    if 'slice' in filter:
        slice = _get_slice(filter.get('slice'))
        if slice: filter['slice'] = slice
    subnets = Subnet.objects.filter(**filter)
    return subnets             
        

    
