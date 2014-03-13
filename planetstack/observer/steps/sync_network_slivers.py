import os
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.network import *

class SyncNetworkSlivers(OpenStackSyncStep):
    requested_interval = 3600
    provides=[NetworkSliver]

    def fetch_pending(self):
        return NetworkSliver.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))

    def call(self, failed=[]):
        networkSlivers = NetworkSliver.objects.all()
        networkSlivers_by_id = {}
        networkSlivers_by_port = {}
        for networkSliver in networkSlivers:
            networkSlivers_by_id[networkSliver.id] = networkSliver
            networkSlivers_by_port[networkSliver.port_id] = networkSliver

        networks = Network.objects.all()
        networks_by_id = {}
        for network in networks:
            networks_by_id[network.network_id] = network

        slivers = Sliver.objects.all()
        slivers_by_instance_id = {}
        for sliver in slivers:
            slivers_by_instance_id[sliver.instance_id] = sliver

        driver = self.driver.admin_driver(caller=sliver.creator, tenant=sliver.slice.name, deployment=sliver.node.deployment.name)
        ports = driver.shell.quantum.list_ports()["ports"]
        for port in ports:
            if port["id"] in networkSlivers_by_port:
                # we already have it
                print "already accounted for port", port["id"]
                continue

            if port["device_owner"] != "compute:nova":
                # we only want the ports that connect to instances
                continue

            network = networks_by_id.get(port['network_id'], None)
            if not network:
                #print "no network for port", port["id"], "network", port["network_id"]
                continue

            sliver = slivers_by_instance_id.get(port['device_id'], None)
            if not sliver:
                print "no sliver for port", port["id"], "device_id", port['device_id']
                continue

            if network.template.sharedNetworkId is not None:
                # If it's a shared network template, then more than one network
                # object maps to the quantum network. We have to do a whole bunch
                # of extra work to find the right one.
                networks = network.template.network_set.all()
                network = None
                for candidate_network in networks:
                    if (candidate_network.owner == sliver.slice):
                        print "found network", candidate_network
                        network = candidate_network

                if not network:
                    print "failed to find the correct network for a shared template for port", port["id"], "network", port["network_id"]
                    continue

            if not port["fixed_ips"]:
                print "port", port["id"], "has no fixed_ips"
                continue

#             print "XXX", port

            ns = NetworkSliver(network=network,
                               sliver=sliver,
                               ip=port["fixed_ips"][0]["ip_address"],
                               port_id=port["id"])
            ns.save()
