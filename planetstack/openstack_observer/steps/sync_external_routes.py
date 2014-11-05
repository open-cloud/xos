import os
import base64
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.site import Deployment

class SyncExternalRoutes(OpenStackSyncStep):
    # XXX what does this provide?
    provides=[]
    requested_interval = 86400 # This step is slow like a pig. Let's run it infrequently

    def call(self, **args):
	deployments = Deployment.objects.all()
	self.driver = self.driver.admin_driver(deployment=deployments[0],tenant='admin')
        routes = self.driver.get_external_routes()
        subnets = self.driver.shell.quantum.list_subnets()['subnets']
        for subnet in subnets:
            try:
                self.driver.add_external_route(subnet, routes)
            except:
                logger.log_exc("failed to add external route for subnet %s" % subnet)
