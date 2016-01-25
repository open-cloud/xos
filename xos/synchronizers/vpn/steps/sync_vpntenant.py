import os
import sys
from django.db.models import Q, F
from synchronizers.base.SyncInstanceUsingAnsible import SyncInstanceUsingAnsible
from services.vpn.models import VPNTenant

parentdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, parentdir)

class SyncVPNTenant(SyncInstanceUsingAnsible):
    """Class for syncing a VPNTenant using Ansible."""
    provides = [VPNTenant]
    observes = VPNTenant
    requested_interval = 0
    template_name = "sync_vpntenant.yaml"
    service_key_name = "/opt/xos/synchronizers/vpn/vpn_private_key"

    def __init__(self, *args, **kwargs):
        super(SyncVPNTenant, self).__init__(*args, **kwargs)

    def fetch_pending(self, deleted):
        if (not deleted):
            objs = VPNTenant.get_tenant_objects().filter(
                Q(enacted__lt=F('updated')) | Q(enacted=None), Q(lazy_blocked=False))
            for tenant in objs:
                self.create_client_script(tenant)
        else:
            objs = VPNTenant.get_deleted_tenant_objects()

        return objs

    def get_extra_attributes(self, o):
        return {"server_key": o.server_key.splitlines(),
                "is_persistent": o.is_persistent,
                "can_view_subnet": o.can_view_subnet,
                "server_address": o.server_address,
                "client_address": o.client_address}

    def create_client_script(self, tenant):
        script = open("/opt/xos/core/static/vpn/" + str(tenant.file_name), 'w')
        # write the key portion
        script.write("printf \"")
        for line in tenant.server_key.splitlines():
            script.write(line + r"\n")
        script.write("\" > static.key\n")
        # write the configuration portion
        script.write("printf \"")
        for line in self.generate_client_conf(tenant).splitlines():
            script.write(line + r"\n")
        script.write("\" > client.conf\n")
        # make sure openvpn is installed
        script.write("apt-get update\n")
        script.write("apt-get install openvpn\n")
        script.write("openvpn client.conf &")
        # close the script
        script.close()

    def generate_client_conf(self, tenant):
        """str: Generates the client configuration to use to connect to this VPN server.

        Args:
            tenant (VPNTenant): The tenant to generate the client configuration for.

        """
        conf = "remote " + str(tenant.nat_ip) + "\n"
        conf += "dev tun\n"
        conf += "ifconfig " + tenant.client_address + " " + tenant.server_address + "\n"
        conf += "secret static.key"
        if tenant.is_persistent:
            conf += "\nkeepalive 10 60\n"
            conf += "ping-timer-rem\n"
            conf += "persist-tun\n"
            conf += "persist-key"

        return conf
