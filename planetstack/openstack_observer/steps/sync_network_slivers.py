import os
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.network import *
from util.logger import Logger, logging

logger = Logger(level=logging.INFO)

class SyncNetworkSlivers(OpenStackSyncStep):
    requested_interval = 0 # 3600
    provides=[NetworkSliver]

    #     The way it works is to enumerate the all of the ports that quantum
    #     has, and then work backward from each port's network-id to determine
    #     which Network is associated from the port.

    def call(self, **args):
        networkSlivers = NetworkSliver.objects.all()
        networkSlivers_by_id = {}
        networkSlivers_by_port = {}
        for networkSliver in networkSlivers:
            networkSlivers_by_id[networkSliver.id] = networkSliver
            networkSlivers_by_port[networkSliver.port_id] = networkSliver

        networks = Network.objects.all()
        networks_by_id = {}
        for network in networks:
            for nd in network.networkdeployments_set.all():
                networks_by_id[nd.net_id] = network

        #logger.info("networks_by_id = ")
        #for (network_id, network) in networks_by_id.items():
        #    logger.info("   %s: %s" % (network_id, network.name))

        slivers = Sliver.objects.all()
        slivers_by_instance_id = {}
        for sliver in slivers:
            slivers_by_instance_id[sliver.instance_id] = sliver

        driver = self.driver.client_driver(caller=sliver.creator, tenant=sliver.slice.name, deployment=sliver.node.deployment.name)
        ports = driver.shell.quantum.list_ports()["ports"]
        for port in ports:
            #logger.info("port %s" % str(port))
            if port["id"] in networkSlivers_by_port:
                # we already have it
                #logger.info("already accounted for port %s" % port["id"])
                continue

            if port["device_owner"] != "compute:nova":
                # we only want the ports that connect to instances
                #logger.info("port %s is not a compute port, it is a %s" % (port["id"], port["device_owner"]))
                continue

            sliver = slivers_by_instance_id.get(port['device_id'], None)
            if not sliver:
                logger.info("no sliver for port %s device_id %s" % (port["id"], port['device_id']))
                continue

            network = networks_by_id.get(port['network_id'], None)
            if not network:
                logger.info("no network for port %s network %s" % (port["id"], port["network_id"]))

                # we know it's associated with a sliver, but we don't know
                # which network it is part of.

                continue

            if network.template.sharedNetworkName:
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
                    logger.info("failed to find the correct network for a shared template for port %s network %s" % (port["id"], port["network_id"]))
                    continue

            if not port["fixed_ips"]:
                logger.info("port %s has no fixed_ips" % port["id"])
                continue

            ip=port["fixed_ips"][0]["ip_address"]
            logger.info("creating NetworkSliver (%s, %s, %s, %s)" % (str(network), str(sliver), ip, str(port["id"])))

            ns = NetworkSliver(network=network,
                               sliver=sliver,
                               ip=ip,
                               port_id=port["id"])
            ns.save()

    def delete_record(self, network_sliver):
        # Nothing to do, this is an OpenCloud object
        pass

