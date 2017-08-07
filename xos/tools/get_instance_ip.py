
# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


#! /usr/bin/env python

import json
import os
import requests
import sys
from optparse import OptionParser

from operator import itemgetter, attrgetter

def get_slice_id(slice_name):
    r = requests.get(SLICES_API + "?name=%s" % slice_name, auth=OPENCLOUD_AUTH)
    if (r.status_code!=200):
        print >> sys.stderr, "Error: Slice REST API failed"
        sys.exit(-1)
    return r.json()[0]["id"]

def get_node_id(host_name):
     r = requests.get(NODES_API, auth=OPENCLOUD_AUTH)
     if (r.status_code!=200):
        print >> sys.stderr, "Error: Node REST API failed"
        sys.exit(-1)
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

    r = requests.get(INSTANCES_API + query_string, auth=OPENCLOUD_AUTH)
    if (r.status_code!=200):
        print >> sys.stderr, "Error: Instance REST API failed"
        sys.exit(-1)
    return r.json()

def get_networks():
    r = requests.get(NETWORKS_API, auth=OPENCLOUD_AUTH)
    if (r.status_code!=200):
        print >> sys.stderr, "Error: Network REST API failed"
        sys.exit(-1)
    return r.json()

def main():
    global OPENCLOUD_AUTH, REST_API, NODES_API, SLICES_API, INSTANCES_API, PORTS_API, NETWORKS_API

    parser = OptionParser(usage="get_instance_ip.py [options] <rest_hostname> <rest_port>", )

    parser.add_option("-u", "--username", dest="username", help="XOS admin username", metavar="NAME", default="padmin@vicci.org")
    parser.add_option("-p", "--password", dest="password", help="XOS admin password", metavar="PASSWORD", default="letmein")
    parser.add_option("-n", "--node", dest="node", help="show instances on node", metavar="HOSTNAME", default=None)
    parser.add_option("-s", "--slice", dest="slice", help="show instances in slice", metavar="SLICENAME", default=None)
    parser.add_option("-N", "--network", dest="filter_network_name", help="filter network name", metavar="NAME", default=None)
    parser.add_option("-b", "--brief", dest="brief", help="only display the IP, nothing else", action="store_true", default=False)

    (options, args) = parser.parse_args(sys.argv[1:])

    if len(args)!=2:
        print >> sys.stderr, "syntax: get_instance_name.py [options] <rest_hostname> <rest_port>"
        sys.exit(-1)

    rest_hostname = args[0]
    rest_port = args[1]

    REST_API="http://%s:%s/api/core/" % (rest_hostname, rest_port)

    NODES_API = REST_API + "nodes/"
    SLICES_API = REST_API + "slices/"
    INSTANCES_API = REST_API + "instances/"
    PORTS_API = REST_API + "ports/"
    NETWORKS_API = REST_API + "networks/"

    OPENCLOUD_AUTH=(options.username, options.password)

    if options.slice:
        slice_id = get_slice_id(options.slice)
    else:
        slice_id = None

    if options.node:
        node_id = get_node_id(hostname)
    else:
        node_id = None
    instances = get_instances(slice_id, node_id)

    networks = get_networks()
    networks_by_id = {}
    for network in networks:
        networks_by_id[network["id"]] = network

    # get (instance_name, ip) pairs for instances with names and ips

    instances = [x for x in instances if x["instance_name"]]
    instances = sorted(instances, key = lambda instance: instance["instance_name"])

    for instance in instances:
        r = requests.get(PORTS_API + "?instance=%s&no_hyperlinks=1" % instance["id"], auth=OPENCLOUD_AUTH)
        ports = r.json()

        for x in ports:
           net_name = networks_by_id.get(x["network"],{"name": "unknown"})["name"]
           if (options.filter_network_name) and (net_name!=options.filter_network_name):
              continue
           if options.brief:
                print x["ip"]
           else:
               print instance["instance_name"], net_name, x["ip"]

if __name__ == "__main__":
    main()

