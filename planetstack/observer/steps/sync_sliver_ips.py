import os
import base64
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.sliver import Sliver

class SyncSliverIps(OpenStackSyncStep):
	provides=[Sliver]
	requested_interval=0
	def fetch_pending(self):
		slivers = Sliver.objects.filter(ip=None)
		return slivers

	def sync_record(self, sliver):
        driver = self.driver.client_driver(tenant=sliver.slice.name)  
		servers = driver.shell.nova.servers.findall(id=sliver.instance_id)
		if not servers:
			return
		server = servers[0]
		ips = server.addresses.get(sliver.slice.name, [])
		if not ips:
			return
		sliver.ip = ips[0]['addr']
		sliver.save()
		logger.info("saved sliver ip: %s %s" % (sliver, ips[0]))
