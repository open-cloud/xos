#! /usr/bin/env python

import json
import os
import requests
import sys

from operator import itemgetter, attrgetter

REST_API="http://alpha.opencloud.us:8000/xos/"

NODES_API = REST_API + "nodes/"
SLICES_API = REST_API + "slices/"
INSTANCES_API = REST_API + "instances/"
PORTS_API = REST_API + "ports/"

opencloud_auth=("demo@onlab.us", "demo")

def get_slice_id(slice_name):
    r = requests.get(SLICES_API + "?name=%s" % slice_name, auth=opencloud_auth)
    return r.json()[0]["id"]

def get_node_id(host_name):
     r = requests.get(NODES_API)
     nodes = r.json()
     for node in nodes:
         if node["name"].lower() == host_name.lower():
             return node["id"]
     print >> sys.stderr, "Error: failed to find node %s" % host_name
     sys.exit(-1)

def get_instances(slice_id=None, node_id=None):
    queries = []
    if slice_id:
        queries.append("slice=%s" % str(slice_id))
    if node_id:
        queries.append("node=%s" % str(node_id))

    if queries:
        query_string = "?" + "&".join(queries)
    else:
        query_string = ""

    r = requests.get(INSTANCES_API + query_string, auth=opencloud_auth)
    return r.json()

def main():
    global opencloud_auth

    if len(sys.argv)!=5:
        print >> sys.stderr, "syntax: get_instance_name.py <username>, <password>, <hostname> <slicename>"
        sys.exit(-1)

    username = sys.argv[1]
    password = sys.argv[2]
    hostname = sys.argv[3]
    slice_name = sys.argv[4]

    opencloud_auth=(username, password)

    slice_id = get_slice_id(slice_name)
    node_id = get_node_id(hostname)
    instances = get_instances(slice_id, node_id)

    # get (instance_name, ip) pairs for instances with names and ips

    instances = [x for x in instances if x["instance_name"]]
    instances = sorted(instances, key = lambda instance: instance["instance_name"])

    # return the last one in the list (i.e. the newest one)

    instance_id = instances[-1]["id"]

    r = requests.get(PORTS_API + "?instance=%s" % instance_id, auth=opencloud_auth)
    ports = r.json()
    ips = [x["ip"] for x in ports]

    # XXX kinda hackish -- assumes private ips start with "10." and nat start with "172."

    # print a public IP if there is one
    for ip in ips:
       if (not ip.startswith("10")) and (not ip.startswith("172")):
           print ip
           return

    # otherwise print a privat ip
    for ip in ips:
       if (not ip.startswith("172")):
           print ip
           return

    # otherwise just print the first one
    print ips[0]

if __name__ == "__main__":
    main()

