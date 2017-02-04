import os
import sys
import base64
from django.db.models import F, Q
from xos.config import Config
from synchronizers.base.syncstep import SyncStep, DeferredException
from core.models import XOS
from xos.logger import Logger, logging
from synchronizers.base.ansible_helper import run_template

# xosbuilder will be in steps/..
parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

from xosbuilder import XOSBuilder

logger = Logger(level=logging.INFO)

class SyncXOS(SyncStep, XOSBuilder):
    provides=[XOS]
    observes=XOS
    requested_interval=0
    playbook = "sync_xos.yaml"

    def __init__(self, **args):
        SyncStep.__init__(self, **args)
        XOSBuilder.__init__(self)

    def sync_record(self, xos):
        logger.info("Sync'ing XOS %s" % xos)

        if not xos.docker_project_name:
            raise Exception("xos.docker_project_name is not set")

        if not xos.db_container_name:
            raise Exception("xos.db_container_name is not set")

        if (not xos.enable_build):
            raise DeferredException("XOS build is currently disabled")

        # We've seen the XOS object get synced before the ServiceController object
        # is synced. This results in the XOS UI container getting built with files
        # from that controller missing. So let's try to defer.
        #
        # It could be argued that we should continue to defer if the ServiceController
        # is in error state, but it is important that a single broken service does
        # not takedown the entirety of XOS.

        for scr in xos.loadable_modules.all():
            if (scr.backend_status is not None) and (scr.backend_status.startswith("0")):
                raise DeferredException("Detected unsynced loadable module. Deferring.")

        self.create_docker_compose()

        dockerfiles = [self.create_ui_dockerfile()]
        tenant_fields = {"dockerfiles": dockerfiles,
                         "build_dir": self.build_dir,
                         "docker_project_name": xos.docker_project_name,
                         "ansible_tag": xos.__class__.__name__ + "_" + str(xos.id)}

        path="XOS"
        res = run_template(self.playbook, tenant_fields, path=path, object=xos)

    def delete_record(self, m):
        pass

    def fetch_pending(self, deleted=False):
        pend = super(SyncXOS, self).fetch_pending(deleted)
        return pend

