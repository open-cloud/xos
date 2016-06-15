import os
import socket
import sys
import base64
import time
from django.db.models import F, Q
from xos.config import Config
from synchronizers.base.syncstep import SyncStep
from synchronizers.base.ansible import run_template_ssh
from synchronizers.base.SyncInstanceUsingAnsible import SyncInstanceUsingAnsible
from core.models import Service, Slice, Tag
from services.vsg.models import VSGService, VCPE_KIND
from services.vtr.models import VTRService, VTRTenant
from services.hpc.models import HpcService, CDNPrefix
from xos.logger import Logger, logging

# hpclibrary will be in steps/..
parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

logger = Logger(level=logging.INFO)

CORD_USE_VTN = getattr(Config(), "networking_use_vtn", False)

class SyncVTRTenant(SyncInstanceUsingAnsible):
    provides=[VTRTenant]
    observes=VTRTenant
    requested_interval=0
    template_name = "sync_vtrtenant.yaml"
    #service_key_name = "/opt/xos/services/vtr/vcpe_private_key"

    def __init__(self, *args, **kwargs):
        super(SyncVTRTenant, self).__init__(*args, **kwargs)

    def fetch_pending(self, deleted):
        if (not deleted):
            objs = VTRTenant.get_tenant_objects().filter(Q(enacted__lt=F('updated')) | Q(enacted=None),Q(lazy_blocked=False))
        else:
            objs = VTRTenant.get_deleted_tenant_objects()

        return objs

    def get_vtr_service(self, o):
        if not o.provider_service:
            return None

        vtrs = VTRService.get_service_objects().filter(id=o.provider_service.id)
        if not vtrs:
            return None

        return vtrs[0]

    def get_vcpe_service(self, o):
        if o.target:
            # o.target is a CordSubscriberRoot
            if o.target.volt and o.target.volt.vcpe:
                vcpes = VSGService.get_service_objects().filter(id=o.target.volt.vcpe.provider_service.id)
                if not vcpes:
                    return None
                return vcpes[0]
        return None

    def get_instance(self, o):
        if o.target and o.target.volt and o.target.volt.vcpe:
            return o.target.volt.vcpe.instance
        else:
            return None

    def get_key_name(self, instance):
        if instance.slice.service and (instance.slice.service.kind==VCPE_KIND):
            # We need to use the vsg service's private key. Onboarding won't
            # by default give us another service's private key, so let's assume
            # onboarding has been configured to add vsg_rsa to the vtr service.
            return "/opt/xos/services/vtr/keys/vsg_rsa"
        else:
            raise Exception("VTR doesn't know how to get the private key for this instance")

    def get_extra_attributes(self, o):
        vtr_service = self.get_vtr_service(o)
        vcpe_service = self.get_vcpe_service(o)

        if not vcpe_service:
            raise Exception("No vcpeservice")

        instance = self.get_instance(o)

        if not instance:
            raise Exception("No instance")

        s_tags = []
        c_tags = []
        if o.target and o.target.volt:
            s_tags.append(o.target.volt.s_tag)
            c_tags.append(o.target.volt.c_tag)

        fields = {"s_tags": s_tags,
                "c_tags": c_tags,
                "isolation": instance.isolation,
                "container_name": "vcpe-%s-%s" % (s_tags[0], c_tags[0]),
                "dns_servers": [x.strip() for x in vcpe_service.dns_servers.split(",")],

                "result_fn": "%s-vcpe-%s-%s" % (o.test, s_tags[0], c_tags[0]),
                "resultcode_fn": "code-%s-vcpe-%s-%s" % (o.test, s_tags[0], c_tags[0]) }

        # add in the sync_attributes that come from the vSG object
        # this will be wan_ip, wan_mac, wan_container_ip, wan_container_mac, ...
        if o.target and o.target.volt and o.target.volt.vcpe:
            for attribute_name in o.target.volt.vcpe.sync_attributes:
                fields[attribute_name] = getattr(o.target.volt.vcpe, attribute_name)

        # add in the sync_attributes that come from the SubscriberRoot object
        if o.target and hasattr(o.target, "sync_attributes"):
            for attribute_name in o.target.sync_attributes:
                fields[attribute_name] = getattr(o.target, attribute_name)

        for attribute_name in o.sync_attributes:
            fields[attribute_name] = getattr(o,attribute_name)

        return fields

    def sync_fields(self, o, fields):
        # the super causes the playbook to be run

        super(SyncVTRTenant, self).sync_fields(o, fields)

    def run_playbook(self, o, fields):
        o.result = ""

        result_fn = os.path.join("/opt/xos/synchronizers/vtr/result", fields["result_fn"])
        if os.path.exists(result_fn):
            os.remove(result_fn)

        resultcode_fn = os.path.join("/opt/xos/synchronizers/vtr/result", fields["resultcode_fn"])
        if os.path.exists(resultcode_fn):
            os.remove(resultcode_fn)

        super(SyncVTRTenant, self).run_playbook(o, fields)

        if os.path.exists(result_fn):
            o.result = open(result_fn).read()

        if os.path.exists(resultcode_fn):
            o.result_code = open(resultcode_fn).read()


    def delete_record(self, m):
        pass
