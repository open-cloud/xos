import os
import sys
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.syncstep import SyncStep
from core.models import Service
from hpc.models import HpcService
from requestrouter.models import RequestRouterService
from util.logger import Logger, logging

# hpclibrary will be in steps/..
parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

from hpclib import HpcLibrary

logger = Logger(level=logging.INFO)

class SyncHpcService(SyncStep, HpcLibrary):
    provides=[HpcService]
    requested_interval=0

    def __init__(self, **args):
        SyncStep.__init__(self, **args)
        HpcLibrary.__init__(self)

    def fetch_pending(self, deleted):
        # Looks like deletion is not supported for this object - Sapan
        if (deleted):
            return []
        else:
            return HpcService.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))

    def sync_record(self, hpc_service):
        logger.info("sync'ing hpc_service %s" % str(hpc_service))
        self.write_slices_file(hpc_service, None)
        hpc_service.save()
