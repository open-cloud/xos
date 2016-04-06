import os
import json
import base64
from django.db.models import F, Q
from xos.config import Config
from ec2_observer.syncstep import SyncStep
from core.models.instance import Instance
from core.models.slice import SlicePrivilege, SliceDeployments
from core.models.network import Network, NetworkSlice, NetworkDeployments
from xos.logger import Logger, logging
from ec2_observer.awslib import *
from core.models.site import *
from core.models.slice import *
from ec2_observer.creds import *
import pdb

logger = Logger(level=logging.INFO)

class SyncInstances(SyncStep):
    provides=[Instance]
    requested_interval=0

    def fetch_pending(self, deletion):
        if deletion:
            object_source = Instance.deleted_objects
        else:
            object_source = Instance.objects

        all_instances = object_source.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))
        my_instances = [] 

        for instance in all_instances:
            sd = SliceDeployments.objects.filter(Q(slice=instance.slice))
            if (sd):
                if (sd.deployment.name=='Amazon EC2'):
                    my_instances.append(instance)
            if (instance.node.deployment.name=='Amazon EC2'):
                my_instances.append(instance)
        return my_instances

    def delete_record(self, instance):
        user = instance.creator
        e = get_creds(user=user, site=user.site)
        result = aws_run('ec2 terminate-instances --instance-ids=%s'%instance.instance_id, env=e)

    def sync_record(self, instance):
        logger.info("sync'ing instance:%s deployment:%s " % (instance, instance.node.deployment),extra=instance.tologdict())

        if not instance.instance_id:
            # public keys
            slice_memberships = SlicePrivilege.objects.filter(slice=instance.slice)
            pubkeys = [sm.user.public_key for sm in slice_memberships if sm.user.public_key]

            if instance.creator.public_key:
                pubkeys.append(instance.creator.public_key)

            if instance.slice.creator.public_key:
                pubkeys.append(instance.slice.creator.public_key) 

            # netowrks
            # include all networks available to the slice and/or associated network templates
            #nics = []
            #networks = [ns.network for ns in NetworkSlice.objects.filter(slice=instance.slice)]  
            #network_deployments = NetworkDeployments.objects.filter(network__in=networks, 
                                                                    #deployment=instance.node.deployment)
            # Gather private networks first. This includes networks with a template that has
            # visibility = private and translation = none
            #for network_deployment in network_deployments:
            #   if network_deployment.network.template.visibility == 'private' and \
            #      network_deployment.network.template.translation == 'none': 
            #       nics.append({'net-id': network_deployment.net_id})
    
            # now include network template
            #network_templates = [network.template.sharedNetworkName for network in networks \
            #                    if network.template.sharedNetworkName]
            #for net in driver.shell.quantum.list_networks()['networks']:
            #   if net['name'] in network_templates: 
            #       nics.append({'net-id': net['id']}) 
            # look up image id

            instance_type = instance.node.name.rsplit('.',1)[0]

            # Bail out of we don't have a key
            key_name = instance.creator.email.lower().replace('@', 'AT').replace('.', '')
            u = instance.creator
            s = u.site
            e = get_creds(user=u, site=s)
            key_sig = aws_run('ec2 describe-key-pairs', env=e)
            ec2_keys = key_sig['KeyPairs']
            key_found = False
            for key in ec2_keys:
                if (key['KeyName']==key_name):
                    key_found = True
                    break

            if (not key_found):
                # set backend_status
                raise Exception('Will not sync instance without key')

            image_id = instance.image.path
            instance_sig = aws_run('ec2 run-instances --image-id %s --instance-type %s --count 1 --key-name %s --placement AvailabilityZone=%s'%(image_id,instance_type,key_name,instance.node.site.name), env=e)
            instance.instance_id = instance_sig['Instances'][0]['InstanceId']
            instance.save()
            state = instance_sig['Instances'][0]['State']['Code']
            if (state==16):
                instance.ip = instance_sig['Instances'][0]['PublicIpAddress']
                instance.save()
            else:
                # This status message should go into backend_status
                raise Exception('Waiting for instance to start')
        else:
            ret = aws_run('ec2 describe-instances --instance-ids %s'%instance.instance_id, env=e)
            state = ret['Reservations'][0]['Instances'][0]['State']['Code']
            if (state==16):
                instance.ip = ret['Reservations'][0]['Instances'][0]['PublicIpAddress']
                instance.save()

