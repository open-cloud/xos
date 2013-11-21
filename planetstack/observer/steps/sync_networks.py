import os
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.network import *
from util.logger import Logger, logging

logger = Logger(level=logging.INFO)

class SyncNetworks(OpenStackSyncStep):
    provides=[Network]
    requested_interval = 0

    def fetch_pending(self):
        return Network.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))

    def save_network(self, network):
        if not network.network_id and network.template.sharedNetworkName:
                network.network_id = network.template.sharedNetworkId

        if not network.network_id:
            network_name = network.name

            # create network
            os_network = self.driver.create_network(network_name, shared=True)
            network.network_id = os_network['id']

            # create router
            router = self.driver.create_router(network_name)
            network.router_id = router['id']

            # create subnet
            next_subnet = self.get_next_subnet()
            cidr = str(next_subnet.cidr)
            ip_version = next_subnet.version
            start = str(next_subnet[2])
            end = str(next_subnet[-2])
            subnet = self.driver.create_subnet(name=network_name,
                                               network_id = network.network_id,
                                               cidr_ip = cidr,
                                               ip_version = ip_version,
                                               start = start,
                                               end = end)
            network.subnet = cidr
            network.subnet_id = subnet['id']
            # add subnet as interface to slice's router
            self.driver.add_router_interface(router['id'], subnet['id'])
            # add external route
            self.driver.add_external_route(subnet)
            logger.info("created private subnet (%s) for network: %s" % (cidr, network))
        else:
            (network.subnet_id, network.subnet) = self.driver.get_network_subnet(network.network_id)
            logger.info("sync'ed subnet (%s) for network: %s" % (network.subnet, network))
            network.save()

    def sync_record(self, network):
        if network.owner and network.owner.creator:
            try:
                # update manager context
                real_driver = self.driver
                self.driver = self.driver.client_driver(network.owner.creator, network.owner.name)
                self.save_network(network)
                self.driver = real_driver
                logger.info("saved network: %s" % (network))
            except Exception,e:
                logger.log_exc("save network failed: %s" % network)    
                raise e

