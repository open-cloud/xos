import os
import sys
import base64
from django.db.models import F, Q
from xos.config import Config
from synchronizers.base.syncstep import SyncStep, DeferredException
from core.models import XOS, XOSComponent
from xos.logger import Logger, logging
from synchronizers.base.ansible import run_template

# xosbuilder will be in steps/..
parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

from xosbuilder import XOSBuilder

logger = Logger(level=logging.INFO)

class SyncXOSComponent(SyncStep, XOSBuilder):
    provides=[XOSComponent]
    observes=XOSComponent
    requested_interval=0

    def __init__(self, **args):
        SyncStep.__init__(self, **args)
        XOSBuilder.__init__(self)

    def sync_record(self, sc):
        logger.info("Sync'ing XOSComponent %s" % sc)

        if sc.xos and (not sc.xos.enable_build):
            raise DeferredException("XOS build is currently disabled")

        unready = self.check_controller_unready(sc)
        if unready:
            raise Exception("Controller %s has unready resources: %s" % (str(sc), ",".join([str(x) for x in unready])))

        # There's nothing to actually do, since there's no synchronizer
        # container for libraries.

    def delete_record(self, m):
        pass

    def fetch_pending(self, deleted=False):
        pend = super(SyncXOSComponent, self).fetch_pending(deleted)
        return pend

