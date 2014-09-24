import os
import sys
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.syncstep import SyncStep
from core.models import Service
from hpc.models import ServiceProvider, ContentProvider, CDNPrefix
from util.logger import Logger, logging

# hpclibrary will be in steps/..
parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

from hpclib import HpcLibrary

logger = Logger(level=logging.INFO)

class SyncCDNPrefix(SyncStep, HpcLibrary):
    provides=[CDNPrefix]
    requested_interval=0

    def __init__(self, **args):
        SyncStep.__init__(self, **args)
        HpcLibrary.__init__(self)

    def fetch_pending(self, deleted):
        self.sanity_check()

        return SyncStep.fetch_pending(self, deleted)

    def sanity_check(self):
        # sanity check to make sure our PS objects have CMI objects behind them
        all_p_ids = [x["cdn_prefix_id"] for x in self.client.onev.ListAll("CDNPrefix")]
        for p in CDNPrefix.objects.all():
            if (p.cdn_prefix_id is not None) and (p.cdn_prefix_id not in all_p_ids):
                logger.info("CDN Prefix %s was not found on CMI" % p.cdn_prefix_id)
                p.cdn_prefix_id=None
                p.save()

    def sync_record(self, cp):
        logger.info("sync'ing cdn prefix %s" % str(cp))

        if (not cp.contentProvider) or (not cp.contentProvider.content_provider_id):
            return

        cpid = cp.contentProvider.content_provider_id

        cp_dict = {"service": "HyperCache", "enabled": cp.enabled, "content_provider_id": cpid, "cdn_prefix": cp.prefix}

        if cp.defaultOriginServer and cp.defaultOriginServer.origin_server_id and cp.defaultOriginServer.url:
            cp_dict["default_origin_server"] = cp.defaultOriginServer.url

        #print cp_dict

        if not cp.cdn_prefix_id:
            id = self.client.onev.Create("CDNPrefix", cp_dict)
            cp.cdn_prefix_id = id
        else:
            self.client.onev.Update("CDNPrefix", cp.cdn_prefix_id, cp_dict)

        cp.save()

    def delete_record(self, m):
        self.client.onev.Delete("CDNPrefix", m.cdn_prefix_id)
