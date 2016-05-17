import os
import requests
import socket
import sys
import base64
from django.db.models import F, Q
from xos.config import Config
from synchronizers.base.syncstep import SyncStep
from core.models import Service
from core.models.service import COARSE_KIND
from services.cord.models import Tenant
from xos.logger import Logger, logging
from requests.auth import HTTPBasicAuth
from services.onos.models import ONOSService

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

    def get_vtn_onos_service(self):
#        vtn_tenant = Tenant.objects.filter(name="VTN_ONOS_app")   # XXX fixme - hardcoded
#        if not vtn_tenant:
#            raise "No VTN Onos App found"
#        vtn_tenant = vtn_tenant[0]
#
#        vtn_service = vtn_tenant.provider_service
        vtn_service = ONOSService.get_service_objects().filter(name="ONOS_CORD")  # XXX fixme - harcoded
        if not vtn_service:
            raise "No VTN Onos Service"

        return vtn_service[0]

    def get_vtn_addr(self):
        vtn_service = self.get_vtn_onos_service()

        if vtn_service.rest_hostname:
            return vtn_service.rest_hostname+":"+str(vtn_service.rest_port)

        if not vtn_service.slices.exists():
            raise "VTN Service has no slices"

        vtn_slice = vtn_service.slices.all()[0]

        if not vtn_slice.instances.exists():
            raise "VTN Slice has no instances"

        vtn_instance = vtn_slice.instances.all()[0]

        return vtn_instance.node.name + ":8181"

    def call(self, **args):
        global glo_saved_vtn_maps

        logger.info("sync'ing vtn services")

        vtn_maps = []
        for service in Service.objects.all():
           for id in service.get_vtn_src_ids():
               dependencies = service.get_vtn_dependencies_ids()
               if dependencies:
                   for dependency in dependencies:
                       if dependency["bidirectional"]:
                           directionality="b"
                       else:
                           directionality="u"
                       vtn_maps.append( (id, dependency["serviceId"], directionality) )

        for vtn_map in glo_saved_vtn_maps:
            if not vtn_map in vtn_maps:
                # call vtn rest api to delete map
                url = "http://" + self.get_vtn_addr() + "/onos/cordvtn/service-dependency/%s/%s/%s" % (vtn_map[0],vtn_map[1], vtn_map[2])

                logger.info( "DELETE %s" % url )
                r = requests.delete(url, auth=HTTPBasicAuth('karaf', 'karaf') )    # XXX fixme - hardcoded auth
                if (r.status_code != 200):
                    raise Exception("Received error from vtn service (%d)" % r.status_code)

        for vtn_map in vtn_maps:
            if not (vtn_map in glo_saved_vtn_maps):
                # call vtn rest api to add map
                url = "http://" + self.get_vtn_addr() + "/onos/cordvtn/service-dependency/%s/%s/%s" % (vtn_map[0], vtn_map[1], vtn_map[2])

                logger.info( "POST %s" % url )
                r = requests.post(url, auth=HTTPBasicAuth('karaf', 'karaf') )    # XXX fixme - hardcoded auth
                if (r.status_code != 200):
                    raise Exception("Received error from vtn service (%d)" % r.status_code)

        glo_saved_vtn_maps = vtn_maps
        # TODO: save this

