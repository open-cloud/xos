import os
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.sliver import Sliver
from core.models.slice import Slice, SlicePrivilege, SliceDeployments
from core.models.network import Network, NetworkSlice, NetworkDeployments
from util.logger import Logger, logging

logger = Logger(level=logging.INFO)

class SyncSlivers(OpenStackSyncStep):
    provides=[Sliver]
    requested_interval=0

    def fetch_pending(self):
        return Sliver.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))

    def sync_record(self, sliver):
        logger.info("sync'ing sliver:%s deployment:%s " % (sliver, sliver.node.deployment))
        metadata_update = {}
        if ("numberCores" in sliver.changed_fields):
            metadata_update["cpu_cores"] = str(sliver.numberCores)

        for tag in sliver.slice.tags.all():
            if tag.name.startswith("sysctl-"):
                metadata_update[tag.name] = tag.value

        if not sliver.instance_id:
            driver = self.driver.client_driver(caller=sliver.creator, tenant=sliver.slice.name, deployment=sliver.deploymentNetwork.name)
            # public keys
            slice_memberships = SlicePrivilege.objects.filter(slice=sliver.slice)
            pubkeys = [sm.user.public_key for sm in slice_memberships if sm.user.public_key]
            if sliver.creator.public_key:
                pubkeys.append(sliver.creator.public_key)
            if sliver.slice.creator.public_key:
                pubkeys.append(sliver.slice.creator.public_key) 
            # netowrks
            # include all networks available to the slice and/or associated network templates
            nics = []
            networks = [ns.network for ns in NetworkSlice.objects.filter(slice=sliver.slice)]   
            network_deployments = NetworkDeployments.objects.filter(network__in=networks, 
                                                                    deployment=sliver.node.deployment)
            # Gather private networks first. This includes networks with a template that has
            # visibility = private and translation = none
            for network_deployment in network_deployments:
                if network_deployment.network.template.visibility == 'private' and \
                   network_deployment.network.template.translation == 'none': 
                    nics.append({'net-id': network_deployment.net_id})
    
            # now include network template
            network_templates = [network.template.sharedNetworkName for network in networks \
                                 if network.template.sharedNetworkName]
            #logger.info("%s %s %s %s" % (driver.shell.quantum.username, driver.shell.quantum.password, driver.shell.quantum.tenant, driver.shell.quantum.url))
            for net in driver.shell.quantum.list_networks()['networks']:
                if net['name'] in network_templates: 
                    nics.append({'net-id': net['id']}) 

            # look up image id
            deployment_driver = self.driver.admin_driver(deployment=sliver.deploymentNetwork.name)
            image_id = None
            images = deployment_driver.shell.glance.get_images()
            for image in images:
                if image['name'] == sliver.image.name:
                    image_id = image['id']
                    
            # look up key name at the deployment
            # create/fetch keypair
            keyname = None
            if sliver.creator.public_key:
                keyname = sliver.creator.email.lower().replace('@', 'AT').replace('.', '') +\
                          sliver.slice.name
                key_fields =  {'name': keyname,
                               'public_key': sliver.creator.public_key}
                driver.create_keypair(**key_fields)

            instance = driver.spawn_instance(name=sliver.name,
                                key_name = keyname,
                                image_id = image_id,
                                hostname = sliver.node.name,
                                pubkeys = pubkeys,
                                nics = nics,
                                userdata = sliver.userData )
            sliver.instance_id = instance.id
            sliver.instance_name = getattr(instance, 'OS-EXT-SRV-ATTR:instance_name')
            sliver.save()    

        if sliver.instance_id and metadata_update:
            driver.update_instance_metadata(sliver.instance_id, metadata_update)

