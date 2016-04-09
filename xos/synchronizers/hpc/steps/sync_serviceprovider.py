import os
import sys
import base64
from django.db.models import F, Q
from xos.config import Config
from synchronizers.base.syncstep import SyncStep
from core.models import Service
from services.hpc.models import ServiceProvider
from xos.logger import Logger, logging

# hpclibrary will be in steps/..
parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

from hpclib import HpcLibrary

logger = Logger(level=logging.INFO)

class SyncServiceProvider(SyncStep, HpcLibrary):
    provides=[ServiceProvider]
    observes=ServiceProvider
    requested_interval=0

    def __init__(self, **args):
        SyncStep.__init__(self, **args)
        HpcLibrary.__init__(self)

    def filter_hpc_service(self, objs):
        hpcService = self.get_hpc_service()

        return [x for x in objs if x.hpcService == hpcService]

    def fetch_pending(self, deleted):
        #self.consistency_check()

        return self.filter_hpc_service(SyncStep.fetch_pending(self, deleted))

    def consistency_check(self):
        # set to true if something changed
        result=False

        # sanity check to make sure our PS objects have CMI objects behind them
        all_sp_ids = [x["service_provider_id"] for x in self.client.onev.ListAll("ServiceProvider")]
        for sp in ServiceProvider.objects.all():
            if (sp.service_provider_id is not None) and (sp.service_provider_id not in all_sp_ids):
                logger.info("Service provider %s was not found on CMI" % sp.service_provider_id)
                sp.service_provider_id=None
                sp.save()
                result = True

        return result

    def sync_record(self, sp):
        logger.info("sync'ing service provider %s" % str(sp),extra=sp.tologdict())
        account_name = self.make_account_name(sp.name)
        sp_dict = {"account": account_name, "name": sp.name, "enabled": sp.enabled}
        if not sp.service_provider_id:
            id = self.client.onev.Create("ServiceProvider", sp_dict)
            sp.service_provider_id = id
        else:
            self.client.onev.Update("ServiceProvider", sp.service_provider_id, sp_dict)

        sp.save()

    def delete_record(self, m):
        if m.service_provider_id is not None:
            self.client.onev.Delete("ServiceProvider", m.service_provider_id)
