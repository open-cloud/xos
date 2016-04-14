import os
import shutil
import sys

from django.db.models import F, Q

from services.vpn.models import VPNService, VPNTenant
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

    def fetch_pending(self, deleted):
        if (not deleted):
            objs = VPNTenant.get_tenant_objects().filter(
                Q(enacted__lt=F('updated')) |
                Q(enacted=None), Q(lazy_blocked=False))
        else:
            objs = VPNTenant.get_deleted_tenant_objects()

        return objs

    def get_extra_attributes(self, tenant):
        return {"is_persistent": tenant.is_persistent,
                "vpn_subnet": tenant.vpn_subnet,
                "server_network": tenant.server_network,
                "clients_can_see_each_other": (
                    tenant.clients_can_see_each_other),
                "port_number": tenant.port_number,
                "protocol": tenant.protocol,
                "pki_dir": tenant.pki_dir
                }

    def sync_fields(self, o, fields):
        o.pki_dir = (VPNService.OPENVPN_PREFIX + "server-" + str(o.id))

        if (not os.path.isdir(o.pki_dir)):
            VPNService.execute_easyrsa_command(o.pki_dir, "init-pki")
            VPNService.execute_easyrsa_command(
                o.pki_dir, "--req-cn=XOS build-ca nopass")

        # Very hacky way to handle VPNs that need to share CAs
        if (o.use_ca_from_id):
            tenant = VPNTenant.get_tenant_objects().filter(
                pk=o.use_ca_from_id)[0]
            shutil.copy2(tenant.pki_dir + "/ca.crt", o.pki_dir)
            shutil.copy2(tenant.pki_dir + "/private/ca.key",
                         o.pki_dir + "/private")

        o.ca_crt = self.get_ca_crt(o)

        # If the server has to be built then we need to build it
        if (not os.path.isfile(o.pki_dir + "/issued/server.crt")):
            VPNService.execute_easyrsa_command(
                o.pki_dir, "build-server-full server nopass")
            VPNService.execute_easyrsa_command(o.pki_dir, "gen-dh")

        # Get the most recent list of revoked clients
        VPNService.execute_easyrsa_command(o.pki_dir, "gen-crl")

        # Super runs the playbook
        super(SyncVPNTenant, self).sync_fields(o, fields)

    def get_ca_crt(self, tenant):
        """str: Generates the ca cert by reading from the ca file"""
        with open(tenant.pki_dir + "/ca.crt") as crt:
            return crt.readlines()
