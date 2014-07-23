import os
import sys
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.syncstep import SyncStep
from core.models import Service
from hpc.models import ServiceProvider
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

    def sync_record(self, sp):
        logger.info("sync'ing service provider %s" % str(sp))
        account_name = self.make_account_name(sp.name)
        print "XXX", sp.name, account_name
        sp_dict = {"account": account_name, "name": sp.name, "enabled": sp.enabled}
        if not sp.service_provider_id:
            id = self.client.onev.Create("ServiceProvider", sp_dict)
            sp.service_provider_id = id
        else:
            self.client.onev.Update("ServiceProvider", sp.service_provider_id, sp_dict)

        sp.save()

    def delete_record(self, m):
        print "XXX delete service provider", m
        self.client.onev.Delete("ServiceProvider", m.service_provider_id)
