import os
import requests
import socket
import sys
import base64
from django.db.models import F, Q
from xos.config import Config
from synchronizers.base.syncstep import SyncStep
from synchronizers.base.ansible import run_template_ssh
from core.models import Service
from services.cord.models import VSGService, VSGTenant, VBNGTenant, VBNGService
from services.hpc.models import HpcService, CDNPrefix
from xos.logger import Logger, logging

# VBNG_API = "http://10.0.3.136:8181/onos/virtualbng/privateip/"

# hpclibrary will be in steps/..
parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

logger = Logger(level=logging.INFO)

class SyncVBNGTenant(SyncStep):
    provides=[VSGTenant]
    observes=VSGTenant
    requested_interval=0

    def __init__(self, **args):
        SyncStep.__init__(self, **args)

    def fetch_pending(self, deleted):
        if (not deleted):
            objs = VBNGTenant.get_tenant_objects().filter(Q(enacted__lt=F('updated')) | Q(enacted=None),Q(lazy_blocked=False))
        else:
            objs = VBNGTenant.get_deleted_tenant_objects()

        return objs

    def defer_sync(self, o, reason):
        logger.info("defer object %s due to %s" % (str(o), reason),extra=o.tologdict())
        raise Exception("defer object %s due to %s" % (str(o), reason))

    def get_vbng_service(self, o):
        if not o.provider_service:
             raise Exception("vBNG tenant %s has no provider_service" % str(o.id))
        services = VBNGService.get_service_objects().filter(id = o.provider_service.id)
        if not services:
             raise Exception("vBNG tenant %s is associated with the wrong kind of provider_service" % str(o.id))
        return services[0]

    def get_vbng_url(self, o):
        service = self.get_vbng_service(o)

        # if the service object specifies a vbng_url, then use it
        if service.vbng_url:
            return service.vbng_url

        # otherwise, see if the service has tenancy in ONOS
        for tenant in service.subscribed_tenants.all():
            if tenant.provider_service and tenant.provider_service.kind == "onos":
                onos_service = tenant.provider_service
                if not onos_service.slices.exists():
                    raise Exception("vBNG service is linked to an ONOSApp, but the App's Service has no slices")
                onos_slice = onos_service.slices.all()[0]
                if not onos_slice.instances.exists():
                    raise Exception("vBNG service is linked to an ONOSApp, but the App's Service's Slice has no instances")
                instance = onos_slice.instances.all()[0]

                #onos_app = ONOSApp.objects.filter(id = tenant.id)
                #instance = onos_app.instance
                #if not instance:
                #    raise Exception("ONOSApp has no instance")

                if not instance.instance_name:
                    raise Exception("vBNG service is linked to an ONOSApp, but the App's Service's Slice's first instance is not instantiated")
                ip = instance.get_network_ip("nat")
                if not ip:
                    raise Exception("vBNG service is linked to an ONOSApp, but the App's Service's Slice's first instance does not have an ip")

                logger.info("Using ip %s from ONOS Instance %s" % (ip, instance),extra=o.tologdict())

                return "http://%s:8181/onos/virtualbng/" % ip

        raise Exception("vBNG service does not have vbng_url set, and is not linked to an ONOSApp")

    def get_private_interface(self, o):
        vcpes = VSGTenant.get_tenant_objects().all()
        vcpes = [x for x in vcpes if (x.vbng is not None) and (x.vbng.id == o.id)]
        if not vcpes:
            raise Exception("No vCPE tenant is associated with vBNG %s" % str(o.id))
        if len(vcpes)>1:
            raise Exception("More than one vCPE tenant is associated with vBNG %s" % str(o.id))

        vcpe = vcpes[0]
        instance = vcpe.instance

        if not instance:
            raise Exception("No instance associated with vBNG %s" % str(o.id))

        if not vcpe.wan_ip:
            self.defer_sync(o, "does not have a WAN IP yet")

        if not vcpe.wan_container_mac:
            # this should never happen; container MAC is computed from WAN IP
            self.defer_sync(o, "does not have a WAN container MAC yet")

        return (vcpe.wan_ip, vcpe.wan_container_mac, vcpe.instance.node.name)

    def sync_record(self, o):
        logger.info("sync'ing VBNGTenant %s" % str(o),extra=o.tologdict())

        if not o.routeable_subnet:
            (private_ip, private_mac, private_hostname) = self.get_private_interface(o)
            logger.info("contacting vBNG service to request mapping for private ip %s mac %s host %s" % (private_ip, private_mac, private_hostname) ,extra=o.tologdict())

            url = self.get_vbng_url(o) + "privateip/%s/%s/%s" % (private_ip, private_mac, private_hostname)
            logger.info( "vbng url: %s" % url ,extra=o.tologdict())
            r = requests.post(url )
            if (r.status_code != 200):
                raise Exception("Received error from bng service (%d)" % r.status_code)
            logger.info("received public IP %s from private IP %s" % (r.text, private_ip),extra=o.tologdict())

            if r.text == "0":
                raise Exception("VBNG service failed to return a routeable_subnet (probably ran out)")

            o.routeable_subnet = r.text
            o.mapped_ip = private_ip
            o.mapped_mac = private_mac
            o.mapped_hostname = private_hostname

        o.save()

    def delete_record(self, o):
        logger.info("deleting VBNGTenant %s" % str(o),extra=o.tologdict())

        if o.mapped_ip:
            private_ip = o.mapped_ip
            logger.info("contacting vBNG service to delete private ip %s" % private_ip,extra=o.tologdict())
            r = requests.delete(self.get_vbng_url(o) + "privateip/%s" % private_ip, )
            if (r.status_code != 200):
                raise Exception("Received error from bng service (%d)" % r.status_code)

