import os
import base64
from collections import defaultdict
from netaddr import IPAddress, IPNetwork
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.network import *
from core.models.slice import *
from core.models.slice import Sliver
from util.logger import Logger, logging

logger = Logger(level=logging.INFO)

class SyncNetworkDeployments(OpenStackSyncStep):
    requested_interval = 0 
    provides=[Networ, NetworkDeployments, Sliver]
    
    def fetch_pending(self):
        # network deployments are not visible to users. We must ensure
        # networks are deployed at all deploymets available to their slices. 
        slice_deployments = SliceDeployments.objects.all()
        slice_deploy_lookup = defaultdict(list)
        for slice_deployment in slice_deployments:
            slice_deploy_lookup[slice_deployment.slice].append(slice_deployment.deployment)
        
        network_deployments = NetworkDeployments.objects.all()
        network_deploy_lookup = defaultdict(list)
        for network_deployment in network_deployments:
            network_deploy_lookup[network_deployment.network].append(network_deployment.deployment)

        for network in Network.objects.filter():
            # ignore networks that have
            # template.visibility = private and template.translation = none
            if network.template.visibility == 'private' and not network.template.translation == 'none':
                continue
            expected_deployments = slice_deploy_lookup[network.owner]
            for expected_deployment in expected_deployments:
                if network not in network_deploy_lookup or \
                  expected_deployment not in network_deploy_lookup[network]:
                    nd = NetworkDeployments(network=network, deployment=expected_deployment)
                    nd.save()
        return NetworkDeployments.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))

    def get_next_subnet(self, deployment=None):
        # limit ourself to 10.0.x.x for now
        valid_subnet = lambda net: net.startswith('10.0')
        driver = self.driver.admin_driver(deployment=deployment)
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
        if not network_deployment.network_id and network_deployment.network.template.sharedNetworkName:
            network_deployment.network_id = network_deployment.network.template.sharedNetworkId

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
        else:
            (network_deployment.subnet_id, network_deployment.subnet) = self.driver.get_network_subnet(network_deployment.net_id)
            logger.info("sync'ed subnet (%s) for network: %s" % (network_deployment.subnet, network_deployment.network))

        network_deployment.save()

    def sync_record(self, network_deployment):
        if network_deployment.network.owner and network_deployment.network.owner.creator:
            try:
                # update manager context
                real_driver = self.driver
                self.driver = self.driver.client_driver(caller=network_deployment.network.owner.creator, 
                                                        tenant=network_deployment.network.owner.name,
                                                        deployment=network_deployment.deployment.name)
                self.save_network_deployment(network_deployment)
                self.driver = real_driver
                logger.info("saved network deployment: %s" % (network_deployment))
            except Exception,e:
                logger.log_exc("save network deployment failed: %s" % network_deployment)
                raise e            
        
          
    
