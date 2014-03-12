import os
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.sliver import Sliver
from core.models.slice import SlicePrivilege

class SyncSlivers(OpenStackSyncStep):
    provides=[Sliver]
    requested_interval=0

    def fetch_pending(self):
        return Sliver.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))

    def get_requested_networks(self, slice):
        network_ids = [x.network_id for x in slice.networks.all()]

        if slice.network_id is not None:
            network_ids.append(slice.network_id)

        networks = []
        for network_id in network_ids:
            networks.append({"net-id": network_id})

        return networks

    def sync_record(self, sliver):
        metadata_update = {}
        if ("numberCores" in sliver.changed_fields):
            metadata_update["cpu_cores"] = str(sliver.numberCores)

        for tag in sliver.slice.tags.all():
            if tag.name.startswith("sysctl-"):
                metadata_update[tag.name] = tag.value

        if not sliver.instance_id:
            nics = self.get_requested_networks(sliver.slice)
            file("/tmp/scott-manager","a").write("slice: %s\nreq: %s\n" % (str(sliver.slice.name), str(nics)))
            slice_memberships = SlicePrivilege.objects.filter(slice=sliver.slice)
            pubkeys = [sm.user.public_key for sm in slice_memberships if sm.user.public_key]
            pubkeys.append(sliver.creator.public_key)
            driver = self.driver.client_driver(caller=sliver.creator, tenant=sliver.slice.name, deployment=sliver.node.deployment.name)
            instance = driver.spawn_instance(name=sliver.name,
                                key_name = sliver.creator.keyname,
                                image_id = sliver.image.image_id,
                                hostname = sliver.node.name,
                                pubkeys = pubkeys,
                                nics = nics )
            sliver.instance_id = instance.id
            sliver.instance_name = getattr(instance, 'OS-EXT-SRV-ATTR:instance_name')

        if sliver.instance_id and metadata_update:
            self.driver.update_instance_metadata(sliver.instance_id, metadata_update)

        sliver.save()    
