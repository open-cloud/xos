import os
import sys
import base64
from django.db.models import F, Q
from xos.config import Config
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
        #self.consistency_check()

        return SyncStep.fetch_pending(self, deleted)

    def consistency_check(self):
        # set to true if something changed
        result=False

        # sanity check to make sure our PS objects have CMI objects behind them
        all_p_ids = [x["cdn_prefix_id"] for x in self.client.onev.ListAll("CDNPrefix")]

        all_p_ids = []
        all_origins = {}
        for x in self.client.onev.ListAll("CDNPrefix"):
            id = x["cdn_prefix_id"]
            all_p_ids.append(id)
            all_origins[id] = x.get("default_origin_server", None)

        for p in CDNPrefix.objects.all():
            if (p.cdn_prefix_id is None):
                continue

            if (p.cdn_prefix_id not in all_p_ids):
                logger.info("CDN Prefix %s was not found on CMI" % p.cdn_prefix_id)
                p.cdn_prefix_id=None
                p.save()
                result = True

            if (p.defaultOriginServer!=None) and (all_origins.get(p.cdn_prefix_id,None) != p.defaultOriginServer.url):
                logger.info("CDN Prefix %s does not have default origin server on CMI" % str(p))
                p.save() # this will set updated>enacted and force observer to re-sync
                result = True

        return result

    def sync_record(self, cp):
        logger.info("sync'ing cdn prefix %s" % str(cp))

        if (not cp.contentProvider) or (not cp.contentProvider.content_provider_id):
            return

        cpid = cp.contentProvider.content_provider_id

        cp_dict = {"service": "HyperCache", "enabled": cp.enabled, "content_provider_id": cpid, "cdn_prefix": cp.prefix}

        if cp.defaultOriginServer and cp.defaultOriginServer.url:
            if (not cp.defaultOriginServer.origin_server_id):
                # It's probably a bad idea to try to set defaultOriginServer before
                # we've crated defaultOriginServer.
                logger.info("   cdn prefix %s is waiting for it's default origin server to get an id" % str(cp))
                return

            cp_dict["default_origin_server"] = cp.defaultOriginServer.url

        #print cp_dict

        if not cp.cdn_prefix_id:
            id = self.client.onev.Create("CDNPrefix", cp_dict)
            cp.cdn_prefix_id = id
        else:
            del cp_dict["content_provider_id"]  # this can't be updated
            del cp_dict["cdn_prefix"] # this can't be updated either
            self.client.onev.Update("CDNPrefix", cp.cdn_prefix_id, cp_dict)

        cp.save()

    def delete_record(self, m):
        if m.cdn_prefix_id is not None:
            self.client.onev.Delete("CDNPrefix", m.cdn_prefix_id)
