import os
import sys
import base64
from django.db.models import F, Q
from xos.config import Config
from synchronizers.base.syncstep import SyncStep
from core.models import XOS
from xos.logger import Logger, logging

# xosbuilder will be in steps/..
parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

from xosbuilder import XOSBuilder

logger = Logger(level=logging.INFO)

class SyncXOS(SyncStep, XOSBuilder):
    provides=[XOS]
    observes=XOS
    requested_interval=0

    def __init__(self, **args):
        SyncStep.__init__(self, **args)
        XOSBuilder.__init__(self)

    def sync_record(self, scr):
        logger.info("Sync'ing XOS %s" % scr)
        self.build_xos()

    def delete_record(self, m):
        pass

    def fetch_pending(self, deleted=False):
        pend = super(SyncXOS, self).fetch_pending(deleted)
        return pend

