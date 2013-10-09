import os
import base64
import random
from datetime import datetime 
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.node import Node
from core.models.deployment import Deployment
from core.models.site import Site

class SyncNodes(OpenStackSyncStep):
    provides=[Node]
    requested_interval=0

    def fetch_pending(self):
        config = Config()
        deployment = Deployment.objects.filter(name=config.plc_deployment)[0]
        login_bases = ['princeton', 'stanford', 'gt', 'uw', 'mpisws']
        sites = Site.objects.filter(login_base__in=login_bases)
        
        # collect local nodes
        nodes = Node.objects.all()
        node_hostnames  = [node.name for node in nodes]

        # collect nova nodes
        # generate list of new nodes
        new_nodes = []
        compute_nodes = self.driver.shell.nova.hypervisors.list()
        for compute_node in compute_nodes:
            if compute_node.hypervisor_hostname not in node_hostnames:
                # pick a random site to add the node to for now
                site_index = random.randint(0, len(sites))
                node = Node(name=compute_node.hypervisor_hostname, 
                            site=sites[site_index], deployment=deployment)
                new_nodes.append(node) 
        
        return new_nodes

    def sync_record(self, node):
        node.save()
          
