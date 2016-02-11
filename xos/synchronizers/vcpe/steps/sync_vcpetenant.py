import hashlib
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
from core.models import Service, Slice
from services.cord.models import VSGService, VSGTenant, VOLTTenant
from services.hpc.models import HpcService, CDNPrefix
from xos.logger import Logger, logging

# hpclibrary will be in steps/..
parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

from broadbandshield import BBS

logger = Logger(level=logging.INFO)

PARENTAL_MECHANISM="dnsmasq"
ENABLE_QUICK_UPDATE=False

class SyncVSGTenant(SyncInstanceUsingAnsible):
    provides=[VSGTenant]
    observes=VSGTenant
    requested_interval=0
    template_name = "sync_vcpetenant.yaml"
    service_key_name = "/opt/xos/synchronizers/vcpe/vcpe_private_key"

    def __init__(self, *args, **kwargs):
        super(SyncVSGTenant, self).__init__(*args, **kwargs)

    def fetch_pending(self, deleted):
        if (not deleted):
            objs = VSGTenant.get_tenant_objects().filter(Q(enacted__lt=F('updated')) | Q(enacted=None),Q(lazy_blocked=False))
        else:
            objs = VSGTenant.get_deleted_tenant_objects()

        return objs

    def get_vcpe_service(self, o):
        if not o.provider_service:
            return None

        vcpes = VSGService.get_service_objects().filter(id=o.provider_service.id)
        if not vcpes:
            return None

        return vcpes[0]

    def get_extra_attributes(self, o):
        # This is a place to include extra attributes that aren't part of the
        # object itself. In the case of vCPE, we need to know:
        #   1) the addresses of dnsdemux, to setup dnsmasq in the vCPE
        #   2) CDN prefixes, so we know what URLs to send to dnsdemux
        #   3) BroadBandShield server addresses, for parental filtering
        #   4) vlan_ids, for setting up networking in the vCPE VM

        vcpe_service = self.get_vcpe_service(o)

        dnsdemux_ip = None
        if vcpe_service.backend_network_label:
            # Connect to dnsdemux using the network specified by
            #     vcpe_service.backend_network_label
            for service in HpcService.objects.all():
                for slice in service.slices.all():
                    if "dnsdemux" in slice.name:
                        for instance in slice.instances.all():
                            for ns in instance.ports.all():
                                if ns.ip and ns.network.labels and (vcpe_service.backend_network_label in ns.network.labels):
                                    dnsdemux_ip = ns.ip
            if not dnsdemux_ip:
                logger.info("failed to find a dnsdemux on network %s" % vcpe_service.backend_network_label)
        else:
            # Connect to dnsdemux using the instance's public address
            for service in HpcService.objects.all():
                for slice in service.slices.all():
                    if "dnsdemux" in slice.name:
                        for instance in slice.instances.all():
                            if dnsdemux_ip=="none":
                                try:
                                    dnsdemux_ip = socket.gethostbyname(instance.node.name)
                                except:
                                    pass
            if not dnsdemux_ip:
                logger.info("failed to find a dnsdemux with a public address")

        dnsdemux_ip = dnsdemux_ip or "none"

        cdn_prefixes = []
        for prefix in CDNPrefix.objects.all():
            cdn_prefixes.append(prefix.prefix)

        # Broadbandshield can either be set up internally, using vcpe_service.bbs_slice,
        # or it can be setup externally using vcpe_service.bbs_server.

        bbs_addrs = []
        if vcpe_service.bbs_slice:
            if vcpe_service.backend_network_label:
                for bbs_instance in vcpe_service.bbs_slice.instances.all():
                    for ns in bbs_instance.ports.all():
                        if ns.ip and ns.network.labels and (vcpe_service.backend_network_label in ns.network.labels):
                            bbs_addrs.append(ns.ip)
            else:
                logger.info("unsupported configuration -- bbs_slice is set, but backend_network_label is not")
            if not bbs_addrs:
                logger.info("failed to find any usable addresses on bbs_slice")
        elif vcpe_service.bbs_server:
            bbs_addrs.append(vcpe_service.bbs_server)
        else:
            logger.info("neither bbs_slice nor bbs_server is configured in the vCPE")

        vlan_ids = []
        s_tags = []
        c_tags = []
        if o.volt:
            vlan_ids.append(o.volt.vlan_id)  # XXX remove this
            s_tags.append(o.volt.s_tag)
            c_tags.append(o.volt.c_tag)

        try:
            full_setup = Config().observer_full_setup
        except:
            full_setup = True

        safe_macs=[]
        if o.volt and o.volt.subscriber:
            for user in o.volt.subscriber.users:
                level = user.get("level",None)
                mac = user.get("mac",None)
                if level in ["G", "PG"]:
                    if mac:
                        safe_macs.append(mac)

        fields = {"vlan_ids": vlan_ids,   # XXX remove this
                "s_tags": s_tags,
                "c_tags": c_tags,
                "dnsdemux_ip": dnsdemux_ip,
                "cdn_prefixes": cdn_prefixes,
                "bbs_addrs": bbs_addrs,
                "full_setup": full_setup,
                "isolation": o.instance.isolation,
                "safe_browsing_macs": safe_macs}

        # add in the sync_attributes that come from the SubscriberRoot object

        if o.volt and o.volt.subscriber and hasattr(o.volt.subscriber, "sync_attributes"):
            for attribute_name in o.volt.subscriber.sync_attributes:
                fields[attribute_name] = getattr(o.volt.subscriber, attribute_name)

        return fields

    def sync_fields(self, o, fields):
        # the super causes the playbook to be run

        super(SyncVSGTenant, self).sync_fields(o, fields)

        # now do all of our broadbandshield stuff...

        service = self.get_vcpe_service(o)
        if not service:
            # Ansible uses the service's keypair in order to SSH into the
            # instance. It would be bad if the slice had no service.

            raise Exception("Slice %s is not associated with a service" % instance.slice.name)

        # Make sure the slice is configured properly
        if (service != o.instance.slice.service):
            raise Exception("Slice %s is associated with some service that is not %s" % (str(instance.slice), str(service)))

        # only enable filtering if we have a subscriber object (see below)
        url_filter_enable = False

        # for attributes that come from CordSubscriberRoot
        if o.volt and o.volt.subscriber:
            url_filter_enable = o.volt.subscriber.url_filter_enable
            url_filter_level = o.volt.subscriber.url_filter_level
            url_filter_users = o.volt.subscriber.users

        if PARENTAL_MECHANISM=="broadbandshield":
            # disable url_filter if there are no bbs_addrs
            if url_filter_enable and (not fields.get("bbs_addrs",[])):
                logger.info("disabling url_filter because there are no bbs_addrs")
                url_filter_enable = False

            if url_filter_enable:
                bbs_hostname = None
                if service.bbs_api_hostname and service.bbs_api_port:
                    bbs_hostname = service.bbs_api_hostname
                else:
                    # TODO: extract from slice
                    bbs_hostname = "cordcompute01.onlab.us"

                if service.bbs_api_port:
                    bbs_port = service.bbs_api_port
                else:
                    bbs_port = 8018

                if not bbs_hostname:
                    logger.info("broadbandshield is not configured")
                else:
                    tStart = time.time()
                    bbs = BBS(o.bbs_account, "123", bbs_hostname, bbs_port)
                    bbs.sync(url_filter_level, url_filter_users)

                    if o.hpc_client_ip:
                        logger.info("associate account %s with ip %s" % (o.bbs_account, o.hpc_client_ip))
                        bbs.associate(o.hpc_client_ip)
                    else:
                        logger.info("no hpc_client_ip to associate")

                    logger.info("bbs update time %d" % int(time.time()-tStart))


    def run_playbook(self, o, fields):
        ansible_hash = hashlib.md5(repr(sorted(fields.items()))).hexdigest()
        quick_update = (o.last_ansible_hash == ansible_hash)

        if ENABLE_QUICK_UPDATE and quick_update:
            logger.info("quick_update triggered; skipping ansible recipe")
        else:
            if o.instance.isolation in ["container", "container_vm"]:
                super(SyncVSGTenant, self).run_playbook(o, fields, "sync_vcpetenant_new.yaml")
            else:
                super(SyncVSGTenant, self).run_playbook(o, fields)

        o.last_ansible_hash = ansible_hash

    def delete_record(self, m):
        pass
