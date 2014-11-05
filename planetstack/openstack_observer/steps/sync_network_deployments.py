import os
import base64
from collections import defaultdict
from netaddr import IPAddress, IPNetwork
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.network import *
from core.models.slice import *
from core.models.sliver import Sliver
from util.logger import Logger, logging

logger = Logger(level=logging.INFO)

class SyncNetworkDeployments(OpenStackSyncStep):
    requested_interval = 0
    provides=[Network, NetworkDeployments, Sliver]

    def fetch_pending(self, deleted):
        if (deleted):
            return NetworkDeployments.deleted_objects.all()
        else:
            return NetworkDeployments.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))

    def get_next_subnet(self, deployment=None):
        # limit ourself to 10.0.x.x for now
        valid_subnet = lambda net: net.startswith('10.0')

        driver = self.driver.admin_driver(deployment=deployment,tenant='admin')
        subnets = driver.shell.quantum.list_subnets()['subnets']
        ints = [int(IPNetwork(subnet['cidr']).ip) for subnet in subnets \
                if valid_subnet(subnet['cidr'])]
        ints.sort()
        if ints:
            last_ip = IPAddress(ints[-1])
        else:
            last_ip = IPAddress('10.0.0.0')
        last_network = IPNetwork(str(last_ip) + "/24")
        next_network = IPNetwork(str(IPAddress(last_network) + last_network.size) + "/24")
        return next_network

    def save_network_deployment(self, network_deployment):
        if (not network_deployment.net_id) and network_deployment.network.template.sharedNetworkName:
            # It's a shared network, try to find the shared network id

            quantum_networks = self.driver.shell.quantum.list_networks(name=network_deployment.network.template.sharedNetworkName)["networks"]
            if quantum_networks:
                logger.info("set shared network id %s" % quantum_networks[0]["id"])
                network_deployment.net_id = quantum_networks[0]["id"]
            else:
                logger.info("failed to find shared network id for deployment")
                return

        # At this point, it must be a private network, so create it if it does
        # not exist.

        if not network_deployment.net_id:
            network_name = network_deployment.network.name

            # create network
            os_network = self.driver.create_network(network_name, shared=True)
            network_deployment.net_id = os_network['id']

            # create router
            #router = self.driver.create_router(network_name)
            #network_deployment.router_id = router['id']

            # create subnet
            next_subnet = self.get_next_subnet(deployment=network_deployment.deployment.name)
            cidr = str(next_subnet.cidr)
            ip_version = next_subnet.version
            start = str(next_subnet[2])
            end = str(next_subnet[-2])
            subnet = self.driver.create_subnet(name=network_name,
                                               network_id = network_deployment.net_id,
                                               cidr_ip = cidr,
                                               ip_version = ip_version,
                                               start = start,
                                               end = end)
            network_deployment.subnet = cidr
            network_deployment.subnet_id = subnet['id']
            # add subnet as interface to slice's router
            #self.driver.add_router_interface(router['id'], subnet['id'])
            # add external route
            #self.driver.add_external_route(subnet)
            logger.info("created private subnet (%s) for network: %s" % (cidr, network_deployment.network))

        # Now, figure out the subnet and subnet_id for the network. This works
        # for both private and shared networks.

        if (not network_deployment.subnet_id) or (not network_deployment.subnet):
            (network_deployment.subnet_id, network_deployment.subnet) = self.driver.get_network_subnet(network_deployment.net_id)
            logger.info("sync'ed subnet (%s) for network: %s" % (network_deployment.subnet, network_deployment.network))

        if (not network_deployment.subnet):
            # this will generate a non-null database constraint error
            #   ... which in turn leads to transaction errors
            # it's probably caused by networks that no longer exist at the
            # quantum level.

            logger.info("null subnet for network %s, skipping save" % network_deployment.network)
            return

        network_deployment.save()

    def sync_record(self, network_deployment):
        if not network_deployment.deployment.admin_user:
            logger.info("deployment %r has no admin_user, skipping" % network_deployment.deployment)
            return

        self.driver = self.driver.admin_driver(deployment=network_deployment.deployment,tenant='admin')
        if network_deployment.network.owner and network_deployment.network.owner.creator:
            try:
                # update manager context
		# Bring back
                self.save_network_deployment(network_deployment)
                logger.info("saved network deployment: %s" % (network_deployment))
            except Exception,e:
                logger.log_exc("save network deployment failed: %s" % network_deployment)
                raise e


    def delete_record(self, network_deployment):
        driver = OpenStackDriver().client_driver(caller=network_deployment.network.owner.creator,
                                                 tenant=network_deployment.network.owner.name,
                                                 deployment=network_deployment.deployment.name)
        if (network_deployment.router_id) and (network_deployment.subnet_id):
            driver.delete_router_interface(network_deployment.router_id, network_deployment.subnet_id)
        if network_deployment.subnet_id:
            driver.delete_subnet(network_deployment.subnet_id)
        if network_deployment.router_id:
            driver.delete_router(network_deployment.router_id)
        if network_deployment.net_id:
            driver.delete_network(network_deployment.net_id)
