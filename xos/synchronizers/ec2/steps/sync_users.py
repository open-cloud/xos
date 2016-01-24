import os
import base64
import random
import time
from datetime import datetime 
from django.db.models import F, Q
from xos.config import Config
from ec2_observer.syncstep import SyncStep
from core.models.user import User
from core.models.site import *
from ec2_observer.awslib import *
from ec2_observer.creds import *
import pdb

class SyncUsers(SyncStep):
    provides=[User]
    requested_interval=0

    def fetch_pending(self, deletion):
        if (deletion):
            return []

        users = User.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))
        
        keys = []
        creds = []
        for u in users:
            e = get_creds(user=u, site=u.site)
            key_sig = aws_run('ec2 describe-key-pairs', env=e)
            ec2_keys = key_sig['KeyPairs']
            creds.append(e)
            keys.append(ec2_keys)
        else:
            ec2_keys = []

        for user,ec2_keys,e in zip(users,keys,creds):
            if (user.public_key): 
                key_name = user.email.lower().replace('@', 'AT').replace('.', '')
                key_found = False

                for key in ec2_keys:
                    if (key['KeyName']==key_name):
                        key_found = True
                        break

                if (not key_found):
                    aws_run('ec2 import-key-pair --key-name %s --public-key-material "%s"'%(key_name, user.public_key),env=e)
                    
        return users

    def sync_record(self, node):
        node.save()
