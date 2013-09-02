import os
import base64
from planetstack.config import Config

class SyncExternalRoutes(SyncStep):
	# XXX what does this provide?
	requested_interval = 86400 # This step is slow like a pig. Let's run it infrequently

	def call(self):
		routes = self.manager.driver.get_external_routes()
        subnets = self.manager.driver.shell.quantum.list_subnets()['subnets']
        for subnet in subnets:
            try:
                self.manager.driver.add_external_route(subnet, routes)
            except:
                logger.log_exc("failed to add external route for subnet %s" % subnet)
