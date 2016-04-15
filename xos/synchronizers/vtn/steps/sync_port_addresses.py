import os
import requests
import socket
import sys
import base64
from django.db.models import F, Q
from xos.config import Config
from synchronizers.base.syncstep import SyncStep
from core.models import Service, Port, Controller, Tag
from core.models.service import COARSE_KIND
from services.cord.models import VSGTenant
from services.cord.models import Tenant
from xos.logger import Logger, logging
from requests.auth import HTTPBasicAuth

# hpclibrary will be in steps/..
parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

logger = Logger(level=logging.INFO)

# XXX should save and load this
glo_saved_vtn_maps = []

class SyncPortAddresses(SyncStep):
    requested_interval = 0 # 3600
    provides=[Port]
    observes=Port

    def __init__(self, **args):
        SyncStep.__init__(self, **args)

    def call(self, **args):
        global glo_saved_vtn_maps

        logger.info("sync'ing vsg tenant to port addresses")

        # build up a dictionary of port-->[wan_addrs] mappings
        port_addrs = {}
        for vsg in VSGTenant.get_tenant_objects().all():
            if not vsg.instance:
                logger.info("skipping vsg %s because it has no instance" % vsg)

            wan_ip = vsg.wan_container_ip
            if not wan_ip:
                logger.info("skipping vsg %s because it has no wan_container_ip" % vsg)

            wan_mac = vsg.wan_container_mac
            if not wan_mac:
                logger.info("skipping vsg %s because it has no wan_container_mac" % vsg)

            lan_network = vsg.get_lan_network(vsg.instance)
            if not lan_network:
                logger.info("skipping vsg %s because it has no lan_network" % vsg)

            lan_port = Port.objects.filter(instance = vsg.instance, network=lan_network)
            if not lan_port:
                logger.info("skipping vsg %s because it has no lan_port" % vsg)
            lan_port = lan_port[0]

            if not lan_port.port_id:
                logger.info("skipping vsg %s because its lan_port has no port_id" % vsg)

            if not (lan_port.pk in port_addrs):
                port_addrs[lan_port.pk] = []
            entry = {"mac_address": wan_mac, "ip_address": wan_ip}
            addr_pairs = port_addrs[lan_port.pk]
            if not entry in addr_pairs:
                 addr_pairs.append(entry)

            # now do the VM_WAN_IP from the instance
            if vsg.instance:
                wan_vm_ip = vsg.wan_vm_ip
                wan_vm_mac = vsg.wan_vm_mac
                entry = {"mac_address": wan_vm_mac, "ip_address": wan_vm_ip}
                if not entry in addr_pairs:
                    addr_pairs.append(entry)

        # Get all ports in all controllers
        ports_by_id = {}
        for controller in Controller.objects.all():
            if not controller.admin_tenant:
                logger.info("controller %s has no admin_tenant" % controller)
                continue
            try:
                driver = self.driver.admin_driver(controller = controller)
                ports = driver.shell.quantum.list_ports()["ports"]
            except:
                logger.log_exc("failed to get ports from controller %s" % controller)
                continue

            for port in ports:
                ports_by_id[port["id"]] = port

        for port_pk in port_addrs.keys():
            port = Port.objects.get(pk=port_pk)
            addr_pairs = port_addrs[port_pk]
            neutron_port = ports_by_id.get(port.port_id,None)
            if not neutron_port:
                logger.info("failed to get neutron port for port %s" % port)
                continue

            ips = [x["ip_address"] for x in addr_pairs]

            changed = False

            # delete addresses in neutron that don't exist in XOS
            aaps = neutron_port.get("allowed_address_pairs", [])
            for aap in aaps[:]:
                if not aap["ip_address"] in ips:
                    logger.info("removing address %s from port %s" % (aap["ip_address"], port))
                    aaps.remove(aap)
                    changed = True

            aaps_ips = [x["ip_address"] for x in aaps]

            # add addresses in XOS that don't exist in neutron
            for addr in addr_pairs:
                if not addr["ip_address"] in aaps_ips:
                    logger.info("adding address %s to port %s" % (addr, port))
                    aaps.append( addr )
                    aaps_ips.append(addr["ip_address"])
                    changed = True

            if changed:
                logger.info("updating port %s" % port)
                driver.shell.quantum.update_port(port.port_id, {"port": {"allowed_address_pairs": aaps}})







