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

    def sync_record(self, cp):
        logger.info("sync'ing cdn prefix %s" % str(cp))

        if (not cp.contentProvider) or (not cp.contentProvider.content_provider_id):
            return

        cpid = cp.contentProvider.content_provider_id

        cp_dict = {"service": "HyperCache", "enabled": cp.enabled, "content_provider_id": cpid, "cdn_prefix": cp.prefix}

        #print cp_dict

        if not cp.cdn_prefix_id:
            id = self.client.onev.Create("CDNPrefix", cp_dict)
            cp.cdn_prefix_id = id
        else:
            self.client.onev.Update("CDNPrefix", cp.cdn_prefix_id, cp_dict)

        cp.save()

    def delete_record(self, m):
        self.client.onev.Delete("CDNPrefix", m.cdn_prefix_id)
