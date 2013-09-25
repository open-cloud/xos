import os
import base64
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.sliver import Sliver

class SyncSlivers(OpenStackSyncStep):
    provides=[Sliver]
    requested_interval=0

    def fetch_pending(self):
        return Sliver.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))

    def sync_record(self, slice):
        if not sliver.instance_id:
            nics = self.get_requested_networks(sliver.slice)
            file("/tmp/scott-manager","a").write("slice: %s\nreq: %s\n" % (str(sliver.slice.name), str(nics)))
            slice_memberships = SliceMembership.objects.filter(slice=sliver.slice)
            pubkeys = [sm.user.public_key for sm in slice_memberships if sm.user.public_key]
            pubkeys.append(sliver.creator.public_key)
            instance = self.driver.spawn_instance(name=sliver.name,
                                key_name = sliver.creator.keyname,
                                image_id = sliver.image.image_id,
                                hostname = sliver.node.name,
                                pubkeys = pubkeys,
                                nics = nics )
            sliver.instance_id = instance.id
            sliver.instance_name = getattr(instance, 'OS-EXT-SRV-ATTR:instance_name')

        if sliver.instance_id and ("numberCores" in sliver.changed_fields):
            self.driver.update_instance_metadata(sliver.instance_id, {"cpu_cores": str(sliver.numberCores)})

        sliver.save()    
