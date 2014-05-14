import os
import json
import socket
import sys
import time

sys.path.append("/opt/planetstack")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "planetstack.settings")
from openstack.manager import OpenStackManager
from core.models import Slice, Sliver, ServiceClass, Reservation, Tag, Network, User, Node, Image, Deployment, Site, NetworkTemplate, NetworkSlice

slice_name_map = {}

def ps_id_to_pl_id(x):
    # Since we don't want the PlanetStack object IDs to conflict with existing
    # PlanetLab object IDs in the CMI, just add 100000 to the PlanetStack object
    # IDs.
    return 100000 + x

def pl_id_to_ps_id(x):
    return x - 100000

def pl_slice_id(slice):
    if slice.name.startswith("princeton_vcoblitz"):
        # 70 is the slice id of princeton_vcoblitz on vicci
        return 70
    else:
        return ps_id_to_pl_id(slice.id)

def ps_slicename_to_pl_slicename(x):
    return slice_name_map.get(x,x)

def filter_fields(src, fields):
    dest = {}
    for (key,value) in src.items():
        if (not fields) or (key in fields):
            dest[key] = value
    return dest

def GetSlices(filter={}):
    ps_slices = Slice.objects.filter(**filter)
    slices = []
    for ps_slice in ps_slices:
        node_ids=[]
        for ps_sliver in ps_slice.slivers.all():
            node_ids.append(ps_id_to_pl_id(ps_sliver.node.id))

        slice = {"instantiation": "plc-instantiated",
                 "description": "planetstack slice",
                 "slice_id": pl_slice_id(ps_slice),
                 "node_ids": node_ids,
                 "url": "planetstack",
                 "max_nodes": 1000,
                 "peer_slice_id": None,
                 "slice_tag_ids": [],
                 "peer_id": None,
                 "site_id": ps_id_to_pl_id(ps_slice.site_id),
                 "name": ps_slicename_to_pl_slicename(ps_slice.name)}

                 # creator_person_id, person_ids, expires, created

        slices.append(slice)
    return slices

def GetNodes(node_ids=None, fields=None):
    if node_ids:
        ps_nodes = Node.objects.filter(id__in=[pl_id_to_ps_id(nid) for nid in node_ids])
    else:
        ps_nodes = Node.objects.all()
    nodes = []
    for ps_node in ps_nodes:
        slice_ids=[]
        for ps_sliver in ps_node.slivers.all():
            slice_ids.append(pl_slice_id(ps_sliver.slice))

        node = {"node_id": ps_id_to_pl_id(ps_node.id),
                "site_id": ps_id_to_pl_id(ps_node.site_id),
                "node_type": "regular",
                "peer_node_id": None,
                "hostname": ps_node.name,
                "conf_file_ids": [],
                "slice_ids": slice_ids,
                "model": "planetstack",
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

def GetSites():
    ps_sites = Site.objects.all()
    sites = []
    for ps_site in ps_sites:
        slice_ids=[]
        for ps_slice in ps_site.slices.all():
            slice_ids.append(pl_slice_id(ps_slice))

        node_ids=[]
        for ps_node in ps_site.nodes.all():
            node_ids.append(ps_id_to_pl_id(ps_node.id))


        site = {"site_id": ps_id_to_pl_id(ps_site.id),
                "node_ids": node_ids,
                "pcu_ids": [],
                "max_slices": 100,
                "max_slivers": 1000,
                "is_public": False,
                "peer_site_id": None,
                "abbrebiated_name": ps_site.abbreviated_name,
                "address_ids": [],
                "name": ps_site.name,
                "url": None,
                "site_tag_ids": [],
                "enabled": True,
                "longitude": float(ps_site.location.longitude),
                "latitude": float(ps_site.location.latitude),
                "slice_ids": slice_ids,
                "login_base": ps_site.login_base,
                "peer_id": None}

                # last_updated, ext_consortium_id, person_ids, date_created

        sites.append(site)

    return sites

def GetInterfaces(slicename, node_ids):
    interfaces = []
    ps_slices = Slice.objects.filter(name=slicename)
    for ps_slice in ps_slices:
        for ps_sliver in ps_slice.slivers.all():
            node_id = ps_id_to_pl_id(ps_sliver.node_id)
            if node_id in node_ids:
                ps_node = ps_sliver.node
                interface = {"node_id": node_id,
                             "ip": socket.gethostbyname(ps_node.name),
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

def find_multi_slicename(orig_slicename):
    """
         Because we sometimes have issues deleting a slice in planetstack and
         creating a new one, allow us to use a prefix match, that way someone
         can put a version number of the end of the slicename
    """
    global slice_name_map
    slices = Slice.objects.filter()
    for slice in slices:
        if slice.name.startswith(orig_slicename):
            slice_name_map[slice.name] = orig_slicename
            return slice.name

    return orig_slicename


def GetConfiguration(name):
    slicename = name["name"]
    if "node_id" in name:
        node_id = name["node_id"]
    else:
        node_id = 0

    slicename = find_multi_slicename(slicename)

    node_sliver_tags = GetTags(slicename, node_id)

    slices = GetSlices({"name": slicename})
    perhost = {}
    allinterfaces = {}
    hostipmap = {}
    nodes = []
    if len(slices)==1:
        slice = slices[0]
        node_ids = slice['node_ids']
        nodes = GetNodes(node_ids, ['hostname', 'node_id', 'site_id'])
        nodemap = {}
        for node in nodes:
            nodemap[node['node_id']]=node['hostname']

        interfaces = GetInterfaces(slicename, node_ids)
        hostipmap = {}
        for interface in interfaces:
            if nodemap[interface['node_id']] not in allinterfaces:
                allinterfaces[nodemap[interface['node_id']]] = []
            interface['interface_tags'] = []
            allinterfaces[nodemap[interface['node_id']]].append(interface)
            if interface['is_primary']:
                hostipmap[nodemap[interface['node_id']]] = interface['ip']

        for nid in node_ids:
            sliver_tags = GetTags(slicename,nid)
            perhost[nodemap[nid]] = sliver_tags

    slivers = GetSlices()
    if node_id != 0:
        slivers = [slice for slice in slivers if (node_id in slice.node_ids)]

    sites = GetSites()
    for site in sites:
        site["site_tags"] = []

    timestamp = int(time.time())
    return {'version': 3,
            'timestamp': timestamp,
            'configuration': node_sliver_tags,
            'allconfigurations':perhost,
            'hostipmap':hostipmap,
            'slivers': slivers,
            'interfaces': allinterfaces,
            'sites': sites,
            'nodes': nodes}

if __name__ == '__main__':
    find_multi_slicename("princeton_vcoblitz")  # set up the mapping for princeton_vcoblitz2 -> princeton_vcoblitz

    slices = GetSlices()
    nodes = GetNodes()

    if ("-d" in sys.argv):
        config = GetConfiguration({"name": "princeton_vcoblitz"})
        print config
        print slices
        print nodes
    else:
        configs={}
        for slicename in ["princeton_vcoblitz"]:
            configs[slicename] = GetConfiguration({"name": slicename})

        file("planetstack_config","w").write(json.dumps(configs))
        file("planetstack_slices","w").write(json.dumps(slices))
        file("planetstack_nodes","w").write(json.dumps(nodes))
