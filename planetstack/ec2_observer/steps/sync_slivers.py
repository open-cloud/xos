import os
import json
import base64
from django.db.models import F, Q
from planetstack.config import Config
from ec2_observer.syncstep import SyncStep
from core.models.sliver import Sliver
from core.models.slice import SlicePrivilege, SliceDeployments
from core.models.network import Network, NetworkSlice, NetworkDeployments
from util.logger import Logger, logging
from ec2_observer.awslib import *
from core.models.site import *
from core.models.slice import *
import pdb

logger = Logger(level=logging.INFO)

class SyncSlivers(SyncStep):
	provides=[Sliver]
	requested_interval=0

	def fetch_pending(self, deletion):
		all_slivers = Sliver.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))
		my_slivers = []	

		for sliver in all_slivers:
			sd = SliceDeployments.objects.filter(Q(slice=sliver.slice))
			if (sd):
				if (sd.deployment.name=='Amazon EC2'):
					my_slivers.append(sliver)
			if (sliver.node.deployment.name=='Amazon EC2'):
				my_slivers.append(sliver)
		return my_slivers

	def sync_record(self, sliver):
		logger.info("sync'ing sliver:%s deployment:%s " % (sliver, sliver.node.deployment))

		if not sliver.instance_id:
			# public keys
			slice_memberships = SlicePrivilege.objects.filter(slice=sliver.slice)
			pubkeys = [sm.user.public_key for sm in slice_memberships if sm.user.public_key]

			if sliver.creator.public_key:
				pubkeys.append(sliver.creator.public_key)

			if sliver.slice.creator.public_key:
				pubkeys.append(sliver.slice.creator.public_key) 

			# netowrks
			# include all networks available to the slice and/or associated network templates
			#nics = []
			#networks = [ns.network for ns in NetworkSlice.objects.filter(slice=sliver.slice)]	
			#network_deployments = NetworkDeployments.objects.filter(network__in=networks, 
																	#deployment=sliver.node.deployment)
			# Gather private networks first. This includes networks with a template that has
			# visibility = private and translation = none
			#for network_deployment in network_deployments:
			#	if network_deployment.network.template.visibility == 'private' and \
			#	   network_deployment.network.template.translation == 'none': 
			#		nics.append({'net-id': network_deployment.net_id})
	
			# now include network template
			#network_templates = [network.template.sharedNetworkName for network in networks \
			#					 if network.template.sharedNetworkName]
			#for net in driver.shell.quantum.list_networks()['networks']:
			#	if net['name'] in network_templates: 
			#		nics.append({'net-id': net['id']}) 
			# look up image id

			instance_type = sliver.node.name.rsplit('.',1)[0]

			# Bail out of we don't have a key
			key_name = sliver.creator.email.lower().replace('@', 'AT').replace('.', '')
			key_sig = aws_run('ec2 describe-key-pairs')
			ec2_keys = key_sig['KeyPairs']
			key_found = False
			for key in ec2_keys:
				if (key['KeyName']==key_name):
					key_found = True
					break

			if (not key_found):
				# set backend_status
				raise Exception('Will not sync sliver without key')

			image_id = sliver.image.path
			instance_sig = aws_run('ec2 run-instances --image-id %s --instance-type %s --count 1 --key-name %s --placement AvailabilityZone=%s'%(image_id,instance_type,key_name,sliver.node.site.name))
			sliver.instance_id = instance_sig['Instances'][0]['InstanceId']
			sliver.save()
			state = instance_sig['Instances'][0]['State']['Code']
			if (state==16):
				sliver.ip = instance_sig['Instances'][0]['PublicIpAddress']
				sliver.save()
			else:
				# This status message should go into backend_status
				raise Exception('Waiting for instance to start')
		else:
			ret = aws_run('ec2 describe-instances --instance-ids %s'%sliver.instance_id)
			state = ret['Reservations'][0]['Instances'][0]['State']['Code']
			if (state==16):
				sliver.ip = ret['Reservations'][0]['Instances'][0]['PublicIpAddress']
				sliver.save()

