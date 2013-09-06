import os
import base64
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.network import *

class SyncNetworks(OpenStackSyncStep):
	provides=[Network]
	requested_interval = 0

	def save_network(self, network):
		if not network.network_id:
			if network.template.sharedNetworkName:
				network.network_id = network.template.sharedNetworkId
				(network.subnet_id, network.subnet) = self.driver.get_network_subnet(network.network_id)
			else:
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

	def sync_record(self, site):
		if network.owner and network.owner.creator:
				try:
					# update manager context
					self.driver.init_caller(network.owner.creator, network.owner.name)
					self.save_network(network)
					logger.info("saved network: %s" % (network))
				except Exception,e:
					logger.log_exc("save network failed: %s" % network)	
					raise e

