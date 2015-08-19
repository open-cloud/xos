#! /usr/bin/env python

import json
import os
import requests
import sys

from operator import itemgetter, attrgetter

opencloud_auth = None

REST_API="http://portal.opencloud.us/xos/"

NODES_API = REST_API + "nodes/"
SITES_API = REST_API + "sites/"
SLICES_API = REST_API + "slices/"
SLIVERS_API = REST_API + "instance/"

def get_nodes_by_site():
    r = requests.get(SITES_API + "?no_hyperlinks=1", auth=opencloud_auth)
    sites_list = r.json()
    sites = {}
    for site in sites_list:
        site["hostnames"] = []
        sites[str(site["id"])] = site

    r = requests.get(NODES_API + "?no_hyperlinks=1", auth=opencloud_auth)
    nodes = r.json()
    for node in nodes:
        site_id = str(node["site"])
        if site_id in sites:
            sites[site_id]["hostnames"].append(node["name"])

    return sites

"""
   WIP

def get_nodes_by_slice():
    r = requests.get(SLICES_API + "?no_hyperlinks=1", auth=opencloud_auth)
    sites_list = r.json()
    slices = {}
    for slice in slices_list:
        slice["hostnames"] = []
        slices[str(slices["id"])] = slice

    r = requests.get(NODES_API + "?no_hyperlinks=1", auth=opencloud_auth)
    nodes_list = r.json()
    nodes = {}
    for node in nodes_list:
        nodes[str(nodes["id"])] = node

    r = requests.get(SLIVERS_API + "?no_hyperlinks=1", auth=opencloud_auth)
    instances = r.json()
    for instances in nodes:
        if instance["node"] not in nodes:
            continue
        if instance["slice"] not in slices:
            continue

        hostname = nodes[instance["node"]].name

        slices[instance["slice"]]["hostnames"].append(hostname)

    return slices
"""

def main():
    global opencloud_auth

    if len(sys.argv)!=3:
        print >> sys.stderr, "syntax: get_instance_name.py <username>, <password>"
        sys.exit(-1)

    username = sys.argv[1]
    password = sys.argv[2]

    opencloud_auth=(username, password)

    sites = get_nodes_by_site()

    for site in sites.values():
        if not site["hostnames"]:
            continue

        print "[%s]" % site["name"]
        for hostname in site["hostnames"]:
            print hostname
        print ""

    print "[all-opencloud:children]"
    for site in sites.values():
        if not site["hostnames"]:
            continue
        print site["name"]

if __name__ == "__main__":
    main()

