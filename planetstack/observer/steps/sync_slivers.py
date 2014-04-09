import os
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.sliver import Sliver
from core.models.slice import SlicePrivilege, SliceDeployments
from core.models.network import NetworkDeployments
from util.logger import Logger, logging

logger = Logger(level=logging.INFO)

class SyncSlivers(OpenStackSyncStep):
    provides=[Sliver]
    requested_interval=0

    def fetch_pending(self):
        return Sliver.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))

    def get_requested_networks(self, slice, deployment):
        requested_networks = []
        networks = slice.networks.all()
        network_deployments = NetworkDeployments.objects.filter(network__in=networks, deployment=deployment)
        requested_networks = [{'net-id': nd.net_id} for nd in network_deployments]
        return requested_networks        

    def sync_record(self, sliver):
        logger.info("sync'ing sliver:%s deployment:%s " % (sliver, sliver.node.deployment))
        metadata_update = {}
        if ("numberCores" in sliver.changed_fields):
            metadata_update["cpu_cores"] = str(sliver.numberCores)

        for tag in sliver.slice.tags.all():
            if tag.name.startswith("sysctl-"):
                metadata_update[tag.name] = tag.value

        if not sliver.instance_id:
            nics = self.get_requested_networks(sliver.slice, sliver.node.deployment)
            file("/tmp/scott-manager","a").write("slice: %s\nreq: %s\n" % (str(sliver.slice.name), str(nics)))
            slice_memberships = SlicePrivilege.objects.filter(slice=sliver.slice)
            pubkeys = [sm.user.public_key for sm in slice_memberships if sm.user.public_key]
            if sliver.creator.public_key:
                pubkeys.append(sliver.creator.public_key)
            driver = self.driver.client_driver(caller=sliver.creator, tenant=sliver.slice.name, deployment=sliver.deploymentNetwork.name)
            # look up image id
            deployment_driver = self.driver.admin_driver(deployment=sliver.deploymentNetwork.name)
            image_id = None
            images = deployment_driver.shell.glance.get_images()
            for image in images:
                if image['name'] == sliver.image.name:
                    image_id = image['id']
                    
            # look up key name at the deployment
            keyname = None
            slice_deployments = SliceDeployments.objects.filter(slice = sliver.slice, 
                                                               deployment = sliver.deploymentNetwork)
            for slice_deployment in slice_deployments:
                if slice_deployment.keyname:
                    keyname = slice_deployment.keyname
                    break 
 
            instance = driver.spawn_instance(name=sliver.name,
                                key_name = keyname,
                                image_id = image_id,
                                hostname = sliver.node.name,
                                pubkeys = pubkeys,
                                nics = nics )
            sliver.instance_id = instance.id
            sliver.instance_name = getattr(instance, 'OS-EXT-SRV-ATTR:instance_name')

        if sliver.instance_id and metadata_update:
            driver.update_instance_metadata(sliver.instance_id, metadata_update)

        sliver.save()    
