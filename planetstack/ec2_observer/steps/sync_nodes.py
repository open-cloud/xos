import os
import base64
import random
import time
from datetime import datetime 
from django.db.models import F, Q
from planetstack.config import Config
from ec2_observer.syncstep import SyncStep
from core.models.node import Node
from core.models.site import *
from ec2_observer.awslib import *
import pdb

class SyncNodes(SyncStep):
	provides=[Node]
	requested_interval=0

	def fetch_pending(self, deletion):
        if (deletion):
            return []

		deployment = Deployment.objects.filter(Q(name="Amazon EC2"))[0]
		current_site_deployments = SiteDeployments.objects.filter(Q(deployment=deployment))

		zone_ret = aws_run('ec2 describe-availability-zones')
		zones = zone_ret['AvailabilityZones']

		# collect local nodes
		instance_types = 'm1.small | m1.medium | m1.large | m1.xlarge | m3.medium | m3.large | m3.xlarge | m3.2xlarge'.split(' | ')

		all_new_nodes = []
		for sd in current_site_deployments:
			s = sd.site
			current_fqns = [n.name for n in s.nodes.all()]
			all_fqns = ['.'.join([n,s.name]) for n in instance_types]
			new_node_names = list(set(all_fqns) - set(current_fqns))

			new_nodes = []
			for node_name in new_node_names:
				node = Node(name=node_name,
							site=s,deployment=deployment)
				new_nodes.append(node)

			all_new_nodes.extend(new_nodes)

		return all_new_nodes
				 

	def sync_record(self, node):
		node.save()
		  
