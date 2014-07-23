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
            self.client.onev.Update("OriginServer", ors.origin_server_id, ors_dict)

        # ... something breaks (analytics) if the URL starts with http://, so we
        # change it in cob after we added it via onev.
        url = url[7:]
        self.client.cob.UpdateContent(ors.origin_server_id, {"url": url})

        ors.save()

    def delete(self, m):
        self.client.onev.Delete("OriginServer", m.origin_server_id)
