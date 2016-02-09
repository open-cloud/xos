import os
import json
import socket
import sys
import time
import traceback
import xmlrpclib

from core.models import Slice, Instance, ServiceClass, Reservation, Tag, Network, User, Node, Image, Deployment, Site, NetworkTemplate, NetworkSlice

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

def ps_id_to_pl_id(x):
    # Since we don't want the XOS object IDs to conflict with existing
    # PlanetLab object IDs in the CMI, just add 100000 to the XOS object
    # IDs.
    return 100000 + x

def pl_id_to_ps_id(x):
    return x - 100000

# slice_remap is a dict of ps_slice_name -> (pl_slice_name, pl_slice_id)

def pl_slice_id(slice, slice_remap={}):
    if slice.name in slice_remap:
        return int(slice_remap[slice.name][1])
    else:
        return ps_id_to_pl_id(slice.id)

def pl_slicename(slice, slice_remap={}):
    if slice.name in slice_remap:
        return slice_remap[slice.name][0]
    else:
        return slice.name

def filter_fields(src, fields):
    dest = {}
    for (key,value) in src.items():
        if (not fields) or (key in fields):
            dest[key] = value
    return dest

def GetSlices(filter={}, slice_remap={}):
    #ps_slices = Slice.objects.filter(**filter)
    ps_slices = Slice.objects.all()
    slices = []
    for ps_slice in ps_slices:
        if (filter) and ("name" in filter):
            remapped_name = slice_remap.get(ps_slice.name, (ps_slice.name,))[0]
            if (remapped_name != filter["name"]):
                continue

        node_ids=[]
        for ps_instance in ps_slice.instances.all():
            node_ids.append(ps_id_to_pl_id(ps_instance.node.id))

        slice = {"instantiation": "plc-instantiated",
                 "description": "XOS slice",
                 "slice_id": pl_slice_id(ps_slice, slice_remap),
                 "node_ids": node_ids,
                 "url": "xos",
                 "max_nodes": 1000,
                 "peer_slice_id": None,
                 "slice_tag_ids": [],
                 "peer_id": None,
                 "site_id": ps_id_to_pl_id(ps_slice.site_id),
                 "name": pl_slicename(ps_slice, slice_remap),
                 "planetstack_name": ps_slice.name}     # keeping planetstack_name for now, to match the modified config.py

                 # creator_person_id, person_ids, expires, created

        slices.append(slice)
    return slices

def GetNodes(node_ids=None, fields=None, slice_remap={}):
    if node_ids:
        ps_nodes = Node.objects.filter(id__in=[pl_id_to_ps_id(nid) for nid in node_ids])
    else:
        ps_nodes = Node.objects.all()
    nodes = []
    for ps_node in ps_nodes:
        slice_ids=[]
        for ps_instance in ps_node.instances.all():
            slice_ids.append(pl_slice_id(ps_instance.slice, slice_remap))

        node = {"node_id": ps_id_to_pl_id(ps_node.id),
                "site_id": ps_id_to_pl_id(ps_node.site_id),
                "node_type": "regular",
                "peer_node_id": None,
                "hostname": ps_node.name.lower(),
                "conf_file_ids": [],
                "slice_ids": slice_ids,
                "model": "xos",
                "peer_id": None,
                "node_tag_ids": []}

                # last_updated, key, boot_state, pcu_ids, node_type, session, last_boot,
                # interface_ids, slice_ids_whitelist, run_level, ssh_rsa_key, last_pcu_reboot,
                # nodegroup_ids, verified, last_contact, boot_nonce, version,
                # last_pcu_configuration, last_download, date_created, ports

        nodes.append(node)

    nodes = [filter_fields(node, fields) for node in nodes]

    return nodes

def GetTags(slicename,node_id):
    return {}

def GetSites(slice_remap={}):
    ps_sites = Site.objects.all()
    sites = []
    for ps_site in ps_sites:
        slice_ids=[]
        for ps_slice in ps_site.slices.all():
            slice_ids.append(pl_slice_id(ps_slice, slice_remap))

        node_ids=[]
        for ps_node in ps_site.nodes.all():
            node_ids.append(ps_id_to_pl_id(ps_node.id))

        if ps_site.location:
            longitude = ps_site.location.longitude
            latitude = ps_site.location.latitude
        else:
            longitude = 0
            latitude = 0

        site = {"site_id": ps_id_to_pl_id(ps_site.id),
                "node_ids": node_ids,
                "pcu_ids": [],
                "max_slices": 100,
                "max_instances": 1000,
                "is_public": False,
                "peer_site_id": None,
                "abbrebiated_name": ps_site.abbreviated_name,
                "address_ids": [],
                "name": ps_site.name,
                "url": None,
                "site_tag_ids": [],
                "enabled": True,
                "longitude": float(longitude),
                "latitude": float(latitude),
                "slice_ids": slice_ids,
                "login_base": ps_site.login_base,
                "peer_id": None}

                # last_updated, ext_consortium_id, person_ids, date_created

        sites.append(site)

    return sites

def GetInterfaces(slicename, node_ids, return_nat=False, return_private=False):
    interfaces = []
    ps_slices = Slice.objects.filter(name=slicename)
    for ps_slice in ps_slices:
        for ps_instance in ps_slice.instances.all():
            node_id = ps_id_to_pl_id(ps_instance.node_id)
            if node_id in node_ids:
                ps_node = ps_instance.node

                ip = socket.gethostbyname(ps_node.name.strip())

                # If the slice has a network that's labeled for hpc_client, then
                # return that network.
                found_labeled_network = False
                for port in ps_instance.ports.all():
                    if (not port.ip):
                        continue
                    if (port.network.owner != ps_slice):
                        continue
                    if port.network.labels and ("hpc_client" in port.network.labels):
                        ip=port.ip
                        found_labeled_network = True

                if not found_labeled_network:
                    # search for a dedicated public IP address
                    for port in ps_instance.ports.all():
                        if (not port.ip):
                            continue
                        template = port.network.template
                        if (template.visibility=="public") and (template.translation=="none"):
                            ip=port.ip

                if return_nat:
                    ip = None
                    for port in ps_instance.ports.all():
                        if (not port.ip):
                            continue
                        template = port.network.template
                        if (template.visibility=="private") and (template.translation=="NAT"):
                            ip=port.ip
                    if not ip:
                        continue

                if return_private:
                    ip = None
                    for port in ps_instance.ports.all():
                        if (not port.ip):
                            continue
                        template = port.network.template
                        if (template.visibility=="private") and (template.translation=="none"):
                            ip=port.ip
                    if not ip:
                        continue

                interface = {"node_id": node_id,
                             "ip": ip,
                             "broadcast": None,
                             "mac": "11:22:33:44:55:66",
                             "bwlimit": None,
                             "network": None,
                             "is_primary": True,
                             "dns1": None,
                             "hostname": None,
                             "netmask": None,
                             "interface_tag_ids": [],
                             "interface_id": node_id,     # assume each node has only one interface
                             "gateway": None,
                             "dns2": None,
                             "type": "ipv4",
                             "method": "dhcp"}
                interfaces.append(interface)
    return interfaces

def GetConfiguration(name, slice_remap={}):
    slicename = name["name"]
    if "node_id" in name:
        node_id = name["node_id"]
    else:
        node_id = 0

    node_instance_tags = GetTags(slicename, node_id)

    slices = GetSlices({"name": slicename}, slice_remap=slice_remap)
    perhost = {}
    allinterfaces = {}
    hostprivmap = {}
    hostipmap = {}
    hostnatmap = {}
    nodes = []
    if len(slices)==1:
        slice = slices[0]
        node_ids = slice['node_ids']
        nodes = GetNodes(node_ids, ['hostname', 'node_id', 'site_id'], slice_remap=slice_remap)
        nodemap = {}
        for node in nodes:
            nodemap[node['node_id']]=node['hostname']

        interfaces = GetInterfaces(slice["planetstack_name"], node_ids)
        hostipmap = {}
        for interface in interfaces:
            if nodemap[interface['node_id']] not in allinterfaces:
                allinterfaces[nodemap[interface['node_id']]] = []
            interface['interface_tags'] = []
            allinterfaces[nodemap[interface['node_id']]].append(interface)
            if interface['is_primary']:
                hostipmap[nodemap[interface['node_id']]] = interface['ip']

        hostnatmap = {}
        interfaces = GetInterfaces(slice["planetstack_name"], node_ids, return_nat=True)
        for interface in interfaces:
            interface['interface_tags'] = []
            hostnatmap[nodemap[interface['node_id']]] = interface['ip']

        hostprivmap = {}
        interfaces = GetInterfaces(slice["planetstack_name"], node_ids, return_private=True)
        for interface in interfaces:
            interface['interface_tags'] = []
            hostprivmap[nodemap[interface['node_id']]] = interface['ip']

        for nid in node_ids:
            instance_tags = GetTags(slicename,nid)
            perhost[nodemap[nid]] = instance_tags

    instances = GetSlices(slice_remap=slice_remap)
    if node_id != 0:
        instances = [slice for slice in instances if (node_id in slice.node_ids)]

    sites = GetSites(slice_remap=slice_remap)
    for site in sites:
        site["site_tags"] = []

    timestamp = int(time.time())
    return {'version': 3,
            'timestamp': timestamp,
            'configuration': node_instance_tags,
            'allconfigurations':perhost,
            'hostipmap':hostipmap,
            'hostnatmap':hostnatmap,
            'hostprivmap':hostprivmap,
            'slivers': instances,
            'interfaces': allinterfaces,
            'sites': sites,
            'nodes': nodes}

DEFAULT_REMAP = {"princeton_vcoblitz2": ["princeton_vcoblitz", 70]}

def HandleGetConfiguration1():
    configs={}
    for slicename in ["princeton_vcoblitz"]:
        configs[slicename] = GetConfiguration({"name": slicename}, DEFAULT_REMAP)
    return configs

def HandleGetNodes1():
    return GetNodes(slice_remap=DEFAULT_REMAP)

def HandleGetSlices1():
    return GetSlices(slice_remap=DEFAULT_REMAP)

def HandleGetConfiguration2(name, slice_remap):
    return GetConfiguration(name, slice_remap=slice_remap)

def HandleGetNodes2(slice_remap):
    return GetNodes(slice_remap=slice_remap)

def HandleGetSlices2(slice_remap):
    return GetSlices(slice_remap=slice_remap)

FUNCS = {"GetConfiguration": HandleGetConfiguration1,
         "GetNodes": HandleGetNodes1,
         "GetSlices": HandleGetSlices1,
         "GetConfiguration2": HandleGetConfiguration2,
         "GetNodes2": HandleGetNodes2,
         "GetSlices2": HandleGetSlices2}

@csrf_exempt
def LegacyXMLRPC(request):
    if request.method == "POST":
        try:
            (args, method) = xmlrpclib.loads(request.body)
            result = None
            if method in FUNCS:
                result = FUNCS[method](*args)
            return HttpResponse(xmlrpclib.dumps((result,), methodresponse=True, allow_none=1))
        except:
            traceback.print_exc()
            return HttpResponseServerError()
    else:
        return HttpResponse("Not Implemented")

if __name__ == '__main__':
    slices = GetSlices(slice_remap = DEFAULT_REMAP)
    nodes = GetNodes(slice_remap = DEFAULT_REMAP)

    config = GetConfiguration({"name": "princeton_vcoblitz"}, slice_remap = DEFAULT_REMAP)
    print config
    print slices
    print nodes

