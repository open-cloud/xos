import os
import base64
import random
import time
from datetime import datetime 
from django.db.models import F, Q
from planetstack.config import Config
from ec2_observer.syncstep import SyncStep
from core.models.user import User
from core.models.site import *
from ec2_observer.awslib import *
import pdb

class SyncUsers(SyncStep):
	provides=[User]
	requested_interval=0

	def fetch_pending(self, deletion):
        if (deletion):
            return []

		users = User.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))
		if (users):
			key_sig = aws_run('ec2 describe-key-pairs')
			ec2_keys = key_sig['KeyPairs']
		else:
			ec2_keys = []

		for user in users:
			if (user.public_key): 
				key_name = user.email.lower().replace('@', 'AT').replace('.', '')
				key_found = False

				for key in ec2_keys:
					if (key['KeyName']==key_name):
						key_found = True
						break

				if (not key_found):
					aws_run('ec2 import-key-pair --key-name %s --public-key-material "%s"'%(key_name, user.public_key))
					
		return users

	def sync_record(self, node):
		node.save()
		  
