import os
import requests
import socket
import sys
import base64
from django.db.models import F, Q
from xos.config import Config
from observer.syncstep import SyncStep
from observer.ansible import run_template_ssh
from core.models import Service
from cord.models import VCPEService, VCPETenant, VBNGTenant, VBNGService
from hpc.models import HpcService, CDNPrefix
from util.logger import Logger, logging

# VBNG_API = "http://10.0.3.136:8181/onos/virtualbng/privateip/"

# hpclibrary will be in steps/..
parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

logger = Logger(level=logging.INFO)

class SyncVBNGTenant(SyncStep):
    provides=[VCPETenant]
    observes=VCPETenant
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
        logger.info("defer object %s due to %s" % (str(o), reason))
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
        if not service.vbng_url:
            raise Exception("vBNG service does not have vbng_url set")
        return service.vbng_url

    def get_private_interface(self, o):
        vcpes = VCPETenant.get_tenant_objects().all()
        vcpes = [x for x in vcpes if (x.vbng is not None) and (x.vbng.id == o.id)]
        if not vcpes:
            raise Exception("No vCPE tenant is associated with vBNG %s" % str(o.id))
        if len(vcpes)>1:
            raise Exception("More than one vCPE tenant is associated with vBNG %s" % str(o.id))

        vcpe = vcpes[0]
        sliver = vcpe.sliver

        if not sliver:
            raise Exception("No sliver associated with vBNG %s" % str(o.id))

        if not vcpe.wan_ip:
            self.defer_sync(o, "does not have a WAN IP yet")

        if not vcpe.wan_mac:
            # this should never happen; WAN MAC is computed from WAN IP
            self.defer_sync(o, "does not have a WAN MAC yet")

        return (vcpe.wan_ip, vcpe.wan_mac, vcpe.sliver.node.name)

    def sync_record(self, o):
        logger.info("sync'ing VBNGTenant %s" % str(o))

        if not o.routeable_subnet:
            (private_ip, private_mac, private_hostname) = self.get_private_interface(o)
            logger.info("contacting vBNG service to request mapping for private ip %s mac %s host %s" % (private_ip, private_mac, private_hostname) )

            url = self.get_vbng_url(o) + "privateip/%s/%s/%s" % (private_ip, private_mac, private_hostname)
            logger.info( "vbng url: %s" % url )
            r = requests.post(url )
            if (r.status_code != 200):
                raise Exception("Received error from bng service (%d)" % r.status_code)
            logger.info("received public IP %s from private IP %s" % (r.text, private_ip))

            if r.text == "0":
                raise Exception("VBNG service failed to return a routeable_subnet (probably ran out)")

            o.routeable_subnet = r.text
            o.mapped_ip = private_ip
            o.mapped_mac = private_mac
            o.mapped_hostname = private_hostname

        o.save()

    def delete_record(self, o):
        logger.info("deleting VBNGTenant %s" % str(o))

        if o.mapped_ip:
            private_ip = o.mapped_ip
            logger.info("contacting vBNG service to delete private ip %s" % private_ip)
            r = requests.delete(self.get_vbng_url(o) + "privateip/%s" % private_ip, )
            if (r.status_code != 200):
                raise Exception("Received error from bng service (%d)" % r.status_code)

