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
from services.cord.models import VSGService, VSGTenant, VOLTTenant, CordSubscriberRoot
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
    service_key_name = "/opt/xos/synchronizers/vtr/vcpe_private_key"

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

        wan_vm_ip=""
        wan_vm_mac=""
        tags = Tag.select_by_content_object(instance).filter(name="vm_wan_addr")
        if tags:
            parts=tags[0].value.split(",")
            if len(parts)!=3:
                raise Exception("vm_wan_addr tag is malformed: %s" % value)
            wan_vm_ip = parts[1]
            wan_vm_mac = parts[2]
        else:
            if CORD_USE_VTN:
                raise Exception("no vm_wan_addr tag for instance %s" % instance)

        fields = {"s_tags": s_tags,
                "c_tags": c_tags,
                "isolation": instance.isolation,
                "wan_container_gateway_mac": vcpe_service.wan_container_gateway_mac,
                "wan_container_gateway_ip": vcpe_service.wan_container_gateway_ip,
                "wan_container_netbits": vcpe_service.wan_container_netbits,
                "wan_vm_mac": wan_vm_mac,
                "wan_vm_ip": wan_vm_ip,
                "container_name": "vcpe-%s-%s" % (s_tags[0], c_tags[0]),
                "dns_servers": [x.strip() for x in vcpe_service.dns_servers.split(",")],

                "result_fn": "%s-vcpe-%s-%s" % (o.test, s_tags[0], c_tags[0]) }

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

        super(SyncVTRTenant, self).run_playbook(o, fields)

        if os.path.exists(result_fn):
            o.result = open(result_fn).read()


    def delete_record(self, m):
        pass
