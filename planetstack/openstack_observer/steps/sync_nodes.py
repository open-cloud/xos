import os
import base64
import random
from datetime import datetime
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.node import Node
from core.models.site import SiteDeployments, Controller, SiteDeployments
from util.logger import Logger, logging

logger = Logger(level=logging.INFO)

class SyncNodes(OpenStackSyncStep):
    provides=[Node]
    requested_interval=0

    def fetch_pending(self, deleted):
        # Nodes come from the back end
        # You can't delete them
        if (deleted):
            return []

        # collect local nodes
        controllers = Controller.objects.all()
        nodes = Node.objects.all()
        node_hostnames = [node.name for node in nodes]

        # fetch all nodes from each controller
        new_nodes = []
        for controller in controllers:
            try:
            	controller_site_deployments = SiteDeployments.objects.filter(controller=controller)[0]
	    except IndexError:
                raise Exception("Controller %s not bound to any site deployments"%controller.name)

            site_deployment = controller_site_deployments.site_deployment
            if (not site_deployment):
                raise Exception('Controller without Site Deployment: %s'%controller.name)

            try:
                driver = self.driver.admin_driver(controller=controller,tenant='admin')
                compute_nodes = driver.shell.nova.hypervisors.list()
            except:
                logger.log_exc("Failed to get nodes from controller %s" % str(controller))
                continue

            for compute_node in compute_nodes:
                if compute_node.hypervisor_hostname not in node_hostnames:
                    # XX TODO:figure out how to correctly identify a node's site.
                    # XX pick the first one
                    node = Node(name=compute_node.hypervisor_hostname,
                                site_deployment=site_deployment)
                    new_nodes.append(node)

        return new_nodes    
                 

    def sync_record(self, node):
        node.save()
          
