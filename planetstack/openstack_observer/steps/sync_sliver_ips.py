import os
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.sliver import Sliver
from util.logger import Logger, logging

class SyncSliverIps(OpenStackSyncStep):
    provides=[Sliver]
    requested_interval=0

    def fetch_pending(self, deleted):
        # Not supported yet
        if (deleted):
            return []
        slivers = Sliver.objects.filter(ip=None)
        return slivers

    def sync_record(self, sliver):
        driver = self.driver.client_driver(tenant=sliver.slice.name,
                                           deployment=sliver.node.deployment.name)
        servers = driver.shell.nova.servers.findall(id=sliver.instance_id)
        if not servers:
            return
        server = servers[0]

        # First try to grab the dedicated public address
        # NOTE: "ext-net" is hardcoded here.
        ip = None
        ext_net_addrs = server.addresses.get("ext-net")
        if ext_net_addrs:
            ip = ext_net_addrs[0]["addr"]

        # If there was no public address, then grab the first address in the
        # list.
        if not ip:
            if server.addresses:
                addrs = server.addresses.values()[0]
                if addrs:
                    ip = addrs[0]["addr"]

        if ip and ip!=sliver.ip:
            sliver.ip = ip
            sliver.save()
            logger.info("saved sliver ip: %s %s" % (sliver, ip))
