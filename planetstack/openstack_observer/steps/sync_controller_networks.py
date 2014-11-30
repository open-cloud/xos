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

class SyncControllerNetworks(OpenStackSyncStep):
    requested_interval = 0
    provides=[Network, ControllerNetworks, Sliver]

    def fetch_pending(self, deleted):
        if (deleted):
            return ControllerNetworks.deleted_objects.all()
        else:
            return ControllerNetworks.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))

    def get_next_subnet(self, controller=None):
        # limit ourself to 10.0.x.x for now
        valid_subnet = lambda net: net.startswith('10.0')

        driver = self.driver.admin_driver(controller=controller,tenant='admin')
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

    def save_controller_network(self, controller_network):
        if (not controller_network.net_id) and controller_network.network.template.sharedNetworkName:
            # It's a shared network, try to find the shared network id

            quantum_networks = self.driver.shell.quantum.list_networks(name=controller_network.network.template.sharedNetworkName)["networks"]
            if quantum_networks:
                logger.info("set shared network id %s" % quantum_networks[0]["id"])
                controller_network.net_id = quantum_networks[0]["id"]
            else:
                logger.info("failed to find shared network id for controller")
                return

        # At this point, it must be a private network, so create it if it does
        # not exist.

        if not controller_network.net_id:
            network_name = controller_network.network.name

            # create network
            os_network = self.driver.create_network(network_name, shared=True)
            controller_network.net_id = os_network['id']

            # create router
            #router = self.driver.create_router(network_name)
            #controller_network.router_id = router['id']

            # create subnet
            next_subnet = self.get_next_subnet(controller=controller_network.controller.name)
            cidr = str(next_subnet.cidr)
            ip_version = next_subnet.version
            start = str(next_subnet[2])
            end = str(next_subnet[-2])
            subnet = self.driver.create_subnet(name=network_name,
                                               network_id = controller_network.net_id,
                                               cidr_ip = cidr,
                                               ip_version = ip_version,
                                               start = start,
                                               end = end)
            controller_network.subnet = cidr
            controller_network.subnet_id = subnet['id']
            # add subnet as interface to slice's router
            #self.driver.add_router_interface(router['id'], subnet['id'])
            # add external route
            #self.driver.add_external_route(subnet)
            logger.info("created private subnet (%s) for network: %s" % (cidr, controller_network.network))

        # Now, figure out the subnet and subnet_id for the network. This works
        # for both private and shared networks.

        if (not controller_network.subnet_id) or (not controller_network.subnet):
            (controller_network.subnet_id, controller_network.subnet) = self.driver.get_network_subnet(controller_network.net_id)
            logger.info("sync'ed subnet (%s) for network: %s" % (controller_network.subnet, controller_network.network))

        if (not controller_network.subnet):
            # this will generate a non-null database constraint error
            #   ... which in turn leads to transaction errors
            # it's probably caused by networks that no longer exist at the
            # quantum level.

            logger.info("null subnet for network %s, skipping save" % controller_network.network)
            return

        controller_network.save()

    def sync_record(self, controller_network):
        logger.info("sync'ing network controller %s for network %s slice %s controller %s" % (controller_network, controller_network.network, str(controller_network.network.owner), controller_network.controller))

        if not controller_network.controller.admin_user:
            logger.info("controller %r has no admin_user, skipping" % controller_network.controller)
            return

        self.driver = self.driver.admin_driver(controller=controller_network.controller,tenant='admin')
        if controller_network.network.owner and controller_network.network.owner.creator:
            try:
                # update manager context
		# Bring back
                self.save_controller_network(controller_network)
                logger.info("saved network controller: %s" % (controller_network))
            except Exception,e:
                logger.log_exc("save network controller failed: %s" % controller_network)
                raise e


    def delete_record(self, controller_network):
        driver = OpenStackDriver().client_driver(caller=controller_network.network.owner.creator,
                                                 tenant=controller_network.network.owner.name,
                                                 controller=controller_network.controller.name)
        if (controller_network.router_id) and (controller_network.subnet_id):
            driver.delete_router_interface(controller_network.router_id, controller_network.subnet_id)
        if controller_network.subnet_id:
            driver.delete_subnet(controller_network.subnet_id)
        if controller_network.router_id:
            driver.delete_router(controller_network.router_id)
        if controller_network.net_id:
            driver.delete_network(controller_network.net_id)
