import os
import base64
from planetstack.config import Config

class SyncSliverIps(OpenStackSyncStep):
	provides=[Sliver]
	requested_interval=0
	def fetch_pending(self):
		slivers = Sliver.objects.filter(ip=None)
		return slivers

	def sync_record(self, sliver):
		self.manager.init_admin(tenant=sliver.slice.name)
		servers = self.manager.driver.shell.nova.servers.findall(id=sliver.instance_id)
		if not servers:
			continue
		server = servers[0]
		ips = server.addresses.get(sliver.slice.name, [])
		if not ips:
			continue
		sliver.ip = ips[0]['addr']
		sliver.save()
		logger.info("saved sliver ip: %s %s" % (sliver, ips[0]))
