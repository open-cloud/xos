import os
import sys
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.syncstep import SyncStep
from core.models import Service
from hpc.models import ServiceProvider, ContentProvider
from util.logger import Logger, logging

# hpclibrary will be in steps/..
parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

from hpclib import HpcLibrary

logger = Logger(level=logging.INFO)

class SyncContentProvider(SyncStep, HpcLibrary):
    provides=[ContentProvider]
    requested_interval=0

    def __init__(self, **args):
        SyncStep.__init__(self, **args)
        HpcLibrary.__init__(self)

    def sync_record(self, cp):
        logger.info("sync'ing content provider %s" % str(cp))
        account_name = self.make_account_name(cp.name)
        print "XXX", cp.name, account_name

        if (not cp.serviceProvider) or (not cp.serviceProvider.service_provider_id):
            return

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
        self.client.onev.Delete("ContentProvider", m.content_provider_id)

