import os
import sys
import base64
from django.db.models import F, Q
from xos.config import Config
from synchronizers.base.syncstep import SyncStep
from core.models import Service
from services.hpc.models import ServiceProvider, ContentProvider
from xos.logger import Logger, logging

# hpclibrary will be in steps/..
parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

from hpclib import HpcLibrary

logger = Logger(level=logging.INFO)

class SyncContentProvider(SyncStep, HpcLibrary):
    provides=[ContentProvider]
    observes=ContentProvider
    requested_interval=0

    def __init__(self, **args):
        SyncStep.__init__(self, **args)
        HpcLibrary.__init__(self)

    def filter_hpc_service(self, objs):
        hpcService = self.get_hpc_service()

        return [x for x in objs if x.serviceProvider.hpcService == hpcService]

    def fetch_pending(self, deleted):
        #self.consistency_check()

        return self.filter_hpc_service(SyncStep.fetch_pending(self, deleted))

    def consistency_check(self):
        # set to true if something changed
        result=False

        # sanity check to make sure our PS objects have CMI objects behind them
        all_cp_ids = [x["content_provider_id"] for x in self.client.onev.ListAll("ContentProvider")]
        for cp in ContentProvider.objects.all():
            if (cp.content_provider_id is not None) and (cp.content_provider_id not in all_cp_ids):
                logger.info("Content provider %s was not found on CMI" % cp.content_provider_id)
                cp.content_provider_id=None
                cp.save()
                result = True

        return result

    def sync_record(self, cp):
        logger.info("sync'ing content provider %s" % str(cp), extra=cp.tologdict())
        account_name = self.make_account_name(cp.name)

        if (not cp.serviceProvider) or (not cp.serviceProvider.service_provider_id):
            raise Exception("ContentProvider %s is linked to a serviceProvider with no id" % str(cp))

        spid = cp.serviceProvider.service_provider_id

        cp_dict = {"account": account_name, "name": cp.name, "enabled": cp.enabled}

        #print cp_dict

        if not cp.content_provider_id:
            cp_dict["service_provider_id"] = spid
            id = self.client.onev.Create("ContentProvider", cp_dict)
            cp.content_provider_id = id
        else:
            self.client.onev.Update("ContentProvider", cp.content_provider_id, cp_dict)

        cp.save()

    def delete_record(self, m):
        if m.content_provider_id is not None:
            self.client.onev.Delete("ContentProvider", m.content_provider_id)

