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
        # collect local nodes
        sites = Site.objects.all()
		one_and_only_deployment = Deployments.objects.all()

        node_hostnames  = [node.name for node in nodes]

		instance_types = 'm1.small | m1.medium | m1.large | m1.xlarge | m3.medium | m3.large | m3.xlarge | m3.2xlarge'.split(' | ')

		all_new_nodes = []
		for s in sites:
			node_names = [n.name for n in s.nodes]
			new_node_names = list(set(instance_types) - set(node_names))
			new_nodes = []
			for node_name in new_node_names:
                node = Node(name=node_name,
                            site=s, deployment=one_and_only_deployment)
				new_nodes.append(node)

			all_new_nodes.extend(new_nodes)

		return all_new_nodes
                 

    def sync_record(self, node):
        node.save()
          
