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

# XXX should save and load this
glo_saved_vtn_maps = []

class SyncTenant(SyncStep):
    provides=[Tenant]
    observes=Tenant
    requested_interval=0

    def __init__(self, **args):
        SyncStep.__init__(self, **args)

    def call(self, **args):
        global glo_saved_vtn_maps

        logger.info("sync'ing vtn services")

        vtn_maps = []
        for service in Service.objects.all():
           for id in service.get_vtn_src_ids():
               dependencies = service.get_vtn_dependencies_ids()
               if dependencies:
                   for dependency in dependencies:
                       vtn_maps.append( (id, dependency) )

        for vtn_map in vtn_maps:
            if not (vtn_map in glo_saved_vtn_maps):
               print "XXX", vtn_map, glo_saved_vtn_maps
               # call vtn rest api to add map
               print "POST /onos/cordvtn/service-dependency/%s/%s" % (vtn_map[0], vtn_map[1])

        for vtn_map in glo_saved_vtn_maps:
            if not vtn_map in vtn_maps:
                # call vtn rest api to delete map
                print "DELETE /onos/cordvtn/service-dependency/%s" % (vtn_map[0],)

        glo_saved_vtn_maps = vtn_maps
        # TODO: save this

