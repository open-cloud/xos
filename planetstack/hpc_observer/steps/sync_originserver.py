import os
import sys
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.syncstep import SyncStep
from core.models import Service
from hpc.models import ServiceProvider, ContentProvider, CDNPrefix, OriginServer
from util.logger import Logger, logging

# hpclibrary will be in steps/..
parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

from hpclib import HpcLibrary

logger = Logger(level=logging.INFO)

class SyncOriginServer(SyncStep, HpcLibrary):
    provides=[OriginServer]
    requested_interval=0

    def __init__(self, **args):
        SyncStep.__init__(self, **args)
        HpcLibrary.__init__(self)

    def fetch_pending(self, deleted):
        self.sanity_check()

        return SyncStep.fetch_pending(self, deleted)

    def sanity_check(self):
        # sanity check to make sure our PS objects have CMI objects behind them
        all_ors_ids = [x["origin_server_id"] for x in self.client.onev.ListAll("OriginServer")]
        for ors in OriginServer.objects.all():
            if (ors.origin_server_id is not None) and (ors.origin_server_id not in all_ors_ids):
                # we have an origin server ID, but it doesn't exist in the CMI
                # something went wrong
                # start over
                logger.info("origin server %s was not found on CMI" % ors.origin_server_id)
                ors.origin_server_id=None
                ors.save()

    def sync_record(self, ors):
        logger.info("sync'ing origin server %s" % str(ors))

        if (not ors.contentProvider) or (not ors.contentProvider.content_provider_id):
            return

        cpid = ors.contentProvider.content_provider_id

        # validation requires URL start with http://
        url = ors.url
        if not url.startswith("http://"):
            url = "http://" + url

        ors_dict = {"authenticated_content": ors.authenticated, "zone_redirects": ors.redirects, "content_provider_id": cpid, "url": url, "service_type": "HyperCache", "caching_type": "Optimistic", "description": ors.description}

        #print os_dict

        if not ors.origin_server_id:
            id = self.client.onev.Create("OriginServer", ors_dict)
            ors.origin_server_id = id
        else:
            id = self.client.onev.Update("OriginServer", ors.origin_server_id, ors_dict)

        # ... something breaks (analytics) if the URL starts with http://, so we
        # change it in cob after we added it via onev.
        url = url[7:]
        self.client.cob.UpdateContent(ors.origin_server_id, {"url": url})

        ors.save()

    def delete(self, m):
        self.client.onev.Delete("OriginServer", m.origin_server_id)
