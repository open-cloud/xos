import os
import sys
import time

from django.db.models import F, Q
from services.vpn.models import VPNTenant
from synchronizers.base.SyncInstanceUsingAnsible import \
    SyncInstanceUsingAnsible

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
        else:
            objs = VPNTenant.get_deleted_tenant_objects()

        return objs

    def get_extra_attributes(self, tenant):
        return {"server_key": tenant.server_key,
                "is_persistent": tenant.is_persistent,
                "vpn_subnet": tenant.vpn_subnet,
                "server_network": tenant.server_network,
                "clients_can_see_each_other": tenant.clients_can_see_each_other,
                "ca_crt": self.get_escaped_ca_crt(tenant),
                "server_crt": tenant.server_crt,
                "dh": tenant.dh
                }

    def get_escaped_ca_crt(self, tenant):
        result = list()
        for line in tenant.ca_crt:
            result.append(line.replace(":", "\\\\u003a"))

        return result

    def create_client_script(self, tenant):
        script = open("/opt/xos/core/static/vpn/" + str(tenant.script), 'w')
        # write the configuration portion
        script.write("printf \"")
        for line in self.generate_client_conf(tenant).splitlines():
            script.write(line + r"\n")
        script.write("\" > client.conf\n")
        script.write("printf \"")
        for line in self.generate_login().splitlines():
            script.write(line + r"\n")
        script.write("\" > login.up\n")
        script.write("printf \"")
        for line in tenant.ca_crt:
            script.write(line.rstrip() + r"\n")
        script.write("\" > ca.crt\n")
        # make sure openvpn is installed
        script.write("apt-get update\n")
        script.write("apt-get install openvpn\n")
        script.write("openvpn client.conf &\n")
        # close the script
        script.close()

    def run_playbook(self, o, fields):
        self.create_client_script(o)
        super(SyncVPNTenant, self).run_playbook(o, fields)

    def generate_login(self):
        return str(time.time()) + "\npassword\n"

    def generate_client_conf(self, tenant):
        """str: Generates the client configuration to use to connect to this VPN server.

        Args:
            tenant (VPNTenant): The tenant to generate the client configuration for.

        """
        conf = ("client\n" +
            "auth-user-pass login.up\n" +
            "dev tun\n" +
            "proto udp\n" +
            "remote " + str(tenant.nat_ip) + " 1194\n" +
            "resolv-retry infinite\n" +
            "nobind\n" +
            "ca ca.crt\n" +
            "comp-lzo\n" +
            "verb 3\n")

        if tenant.is_persistent:
            conf += "persist-tun\n"
            conf += "persist-key\n"

        return conf
