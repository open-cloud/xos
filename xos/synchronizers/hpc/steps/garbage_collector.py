import os
import sys
import base64
import traceback
from collections import defaultdict
from django.db.models import F, Q
from xos.config import Config
from xos.logger import Logger, logging
from synchronizers.base.syncstep import SyncStep
from services.hpc.models import ServiceProvider, ContentProvider, CDNPrefix, OriginServer
from core.models import *

# hpclibrary will be in steps/..
parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

from hpclib import HpcLibrary

logger = Logger(level=logging.INFO)

class GarbageCollector(SyncStep, HpcLibrary):
#    requested_interval = 86400
    requested_interval = 0
    provides=[]

    def __init__(self, **args):
        SyncStep.__init__(self, **args)
        HpcLibrary.__init__(self)

    def call(self, **args):
        logger.info("running garbage collector")
        try:
            self.gc_originservers()
            self.gc_cdnprefixes()
            self.gc_contentproviders()
            self.gc_serviceproviders()
        except:
            traceback.print_exc()

    def gc_onev(self, ps_class, ps_idField, onev_className, onev_idField):
        # get the CMI's objects
        onev_objs = self.client.onev.ListAll(onev_className)

        # get the data model's objects,
        ps_objs = ps_class.objects.filter(enacted__isnull=False)
        ps_ids = [str(getattr(x,ps_idField,None)) for x in ps_objs]

        # for each onev object, if it's id does not exist in a data model
        # object, then delete it.
        for onev_obj in onev_objs:
            onev_id = onev_obj[onev_idField]
            if str(onev_id) not in ps_ids:
                logger.info("garbage collecting %s %s" % (onev_className, str(onev_id)))
                self.client.onev.Delete(onev_className, onev_id)

    def gc_originservers(self):
        self.gc_onev(OriginServer, "origin_server_id", "OriginServer", "origin_server_id")

    def gc_cdnprefixes(self):
        self.gc_onev(CDNPrefix, "cdn_prefix_id", "CDNPrefix", "cdn_prefix_id")

    def gc_contentproviders(self):
        self.gc_onev(ContentProvider, "content_provider_id", "ContentProvider", "content_provider_id")

    def gc_serviceproviders(self):
        self.gc_onev(ServiceProvider, "service_provider_id", "ServiceProvider", "service_provider_id")

