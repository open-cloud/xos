import os
import json
import sys
import time

sys.path.append("/opt/planetstack")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "planetstack.settings")
from openstack.manager import OpenStackManager
from core.models import Slice, Sliver, ServiceClass, Reservation, Tag, Network, User, Node, Image, Deployment, Site, NetworkTemplate, NetworkSlice

def ps_id_to_pl_id(x):
    # Since we don't want the PlanetStack object IDs to conflict with existing
    # PlanetLab object IDs in the CMI, just add 100000 to the PlanetStack object
    # IDs.
    return 100000 + x

def pl_id_to_ps_id(x):
    return x - 100000

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
                 "slice_id": ps_id_to_pl_id(ps_slice.id),
                 "node_ids": node_ids,
                 "url": "planetstack",
                 "max_nodes": 1000,
                 "peer_slice_id": None,
                 "slice_tag_ids": [],
                 "peer_id": None,
                 "site_id": ps_id_to_pl_id(ps_slice.site_id),
                 "name": ps_slice.name}

                 # creator_person_id, person_ids, expires, created

        slices.append(slice)
    return slices

def GetNodes(node_ids, fields=None):
    ps_nodes = Node.objects.filter(id__in=[pl_id_to_ps_id(nid) for nid in node_ids])
    nodes = []
    for ps_node in ps_nodes:
        slice_ids=[]
        for ps_sliver in ps_node.slivers.all():
            slice_ids.append(ps_id_to_pl_id(ps_sliver.slice.id))

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
            slice_ids.append(ps_id_to_pl_id(ps_slice.id))

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


def GetConfiguration(name):
    slicename = name["name"]
    if "node_id" in name:
        node_id = name["node_id"]
    else:
        node_id = 0

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

        # interfaces

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
    print GetConfiguration({"name": "smbaker-coblitz"})



