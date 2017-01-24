import os
import sys
import base64
from django.db.models import F, Q
from xos.config import Config
from synchronizers.base.syncstep import SyncStep
from core.models import Service, ServiceController, ServiceControllerResource
from xos.logger import Logger, logging

# xosbuilder will be in steps/..
parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

from xosbuilder import XOSBuilder

logger = Logger(level=logging.INFO)

class SyncServiceControllerResource(SyncStep, XOSBuilder):
    provides=[ServiceControllerResource]
    observes=ServiceControllerResource
    requested_interval=0

    def __init__(self, **args):
        SyncStep.__init__(self, **args)
        XOSBuilder.__init__(self)

    def sync_record(self, scr):
        logger.info("Sync'ing ServiceControllerResource %s" % scr)
        self.download_resource(scr)

        # TODO: The following should be redone with watchers

        if scr.loadable_module and scr.loadable_module.xos:
            # Make sure the xos UI is resynced
            xos = scr.loadable_module.xos
            xos.save(update_fields=["updated"], always_update_timestamp=True)

        if (scr.kind=="models") and scr.loadable_module and (scr.loadable_module.name != "openstack"):
            # Make sure the openstack controller is restarted. This is necessary
            # as the OpenStack controller is the only one that handles model
            # policies.
            os_scr = ServiceController.objects.filter(name="openstack")
            if os_scr:
                os_scr = os_scr[0]
                os_scr.save(update_fields=["updated"], always_update_timestamp=True)

    def delete_record(self, m):
        pass

    def fetch_pending(self, deleted=False):
        pend = super(SyncServiceControllerResource, self).fetch_pending(deleted)
        return pend

