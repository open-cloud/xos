import os
import sys
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.syncstep import SyncStep
from core.models import Service
from hpc.models import ServiceProvider
from requestrouter.models import RequestRouterService
from util.logger import Logger, logging

# hpclibrary will be in steps/..
parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

from hpclib import HpcLibrary

logger = Logger(level=logging.INFO)

class SyncServiceProvider(SyncStep, HpcLibrary):
    provides=[ServiceProvider]
    requested_interval=0

    def __init__(self, **args):
        SyncStep.__init__(self, **args)
        HpcLibrary.__init__(self)

    def fetch_pending(self):
        return ServiceProvider.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))

    def sync_record(self, sp):
        logger.info("sync'ing service provider %s" % str(sp))
        account_name = self.make_account_name(sp.name)
        print "XXX", sp.name, account_name
        if not sp.service_provider_id:
            id = self.client.onev.Create("ServiceProvider", {"account": account_name, "name": sp.name, "enabled": sp.enabled})
            sp.service_provider_id = id
        else:
            self.client.onev.Update("ServiceProvider", {"account": account_name, "name": sp.name, "enabled": sp.enabled})

        sp.save()
