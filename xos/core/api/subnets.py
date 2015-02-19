import commands
from types import StringTypes
from openstack.client import OpenStackClient
from openstack.driver import OpenStackDriver
from core.api.auth import auth_check
from core.models import Subnet
from core.api.slices import _get_slices


def _get_subnets(filter):
    if isinstance(filter, StringTypes) and filter.isdigit():
        filter = int(filter)
    if isinstance(filter, int):
        subnets = Subnet.objects.filter(id=filter)
    elif isinstance(filter, StringTypes):
        # the name is the subnet's slice's name
        slices = _get_slices(filter)
        slice = None
        if slices: slice=slices[0]
        subnets = Subnet.objects.filter(slice=slice)
    elif isinstance(filter, dict):
        subnets = Subnet.objects.filter(**filter)
    else:
        subnets = []
    return subnets

def add_subnet(auth, fields):
    driver = OpenStackDriver(client = auth_check(auth))
    slices = _get_slices(fields.get('slice')) 
    if slices: fields['slice'] = slices[0]     
    subnet = Subnet(**fields)
    # create quantum subnet
    quantum_subnet = driver.create_subnet(name= subnet.slice.name,
                                          network_id=subnet.slice.network_id,
                                          cidr_ip = subnet.cidr,
                                          ip_version=subnet.ip_version,
                                          start = subnet.start,
                                          end = subnet.end)
    subnet.subnet_id=quantum_subnet['id']
    ## set dns servers
    #driver.update_subnet(subnet.id, {'dns_nameservers': ['8.8.8.8', '8.8.4.4']})

    # add subnet as interface to slice's router
    try: driver.add_router_interface(subnet.slice.router_id, subnet.subnet_id)
    except: pass         
    #add_route = 'route add -net %s dev br-ex gw 10.100.0.5' % self.cidr
    commands.getstatusoutput(add_route)    
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
        #del_route = 'route del -net %s' % subnet.cidr
    commands.getstatusoutput(del_route)
    return 1

def get_subnets(auth, filter={}):
    client = auth_check(auth)
    if 'slice' in filter:
        slice = _get_slice(filter.get('slice'))
        if slice: filter['slice'] = slice
    subnets = Subnet.objects.filter(**filter)
    return subnets             
        

    
