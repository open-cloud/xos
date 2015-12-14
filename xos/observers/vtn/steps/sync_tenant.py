import os
import requests
import socket
import sys
import base64
from django.db.models import F, Q
from xos.config import Config
from observer.syncstep import SyncStep
from core.models import Service
from core.models.service import COARSE_KIND
from cord.models import Tenant
from util.logger import Logger, logging

# hpclibrary will be in steps/..
parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

logger = Logger(level=logging.INFO)

class SyncTenant(SyncStep):
    provides=[Tenant]
    observes=Tenant
    requested_interval=0

    def __init__(self, **args):
        SyncStep.__init__(self, **args)
        self.saved_vtn_maps = []  # TODO: load this

    def call(self, **args):
        logger.info("sync'ing vtn services")
        for service in Service.objects.all():
           for id in service.get_vtn_src_ids():
               dependencies = service.get_vtn_dependencies_ids()
               if dependencies:
                   for dependency in dependencies:
                       vtn_maps.append( (id, dependency) )

        for vtn_map in vtn_maps:
            if not (vtn_map in self.saved_vtn_maps):
               pass # call vtn rest api to add map

        for vtn_map in self.saved_vtn_maps:
            if not vtn_map in vtn_maps:
                pass # call vtn rest api to delete map

        self.saved_vtn_maps = vtn_maps
        # TODO: save this

