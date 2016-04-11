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


    def sync_fields(self, tenant, fields):
        tenant.pki_dir = (
            VPNService.OPENVPN_PREFIX + "server-" + str(result.id))

        if (not os.path.isdir(tenant.pki_dir)):
            VPNService.execute_easyrsa_command(
                tenant.pki_dir, "init-pki")
            if (tenant.use_ca_from[0]):
                shutil.copy2(
                    tenant.use_ca_from[0].pki_dir + "/ca.crt",
                    tenant.pki_dir)
                shutil.copy2(
                    tenant.use_ca_from[0].pki_dir + "/private/ca.key",
                    tenant.pki_dir + "/private")
            else:
                VPNService.execute_easyrsa_command(
                    tenant.pki_dir, "--req-cn=XOS build-ca nopass")
        elif (tenant.use_ca_from[0]):
            shutil.copy2(
                tenant.use_ca_from[0].pki_dir + "/ca.crt",
                tenant.pki_dir)
            shutil.copy2(
                tenant.use_ca_from[0].pki_dir + "/private/ca.key",
                tenant.pki_dir + "/private")

        tenant.ca_crt = tenant.generate_ca_crt()

        if (not os.path.isfile(tenant.pki_dir + "/issued/server.crt")):
            VPNService.execute_easyrsa_command(
                tenant.pki_dir, "build-server-full server nopass")

        if (not os.path.isfile(tenant.pki_dir + "crl.pem")):
            VPNService.execute_easyrsa_command(tenant.pki_dir, "gen-crl")

        if (not os.path.isfile(tenant.pki_dir + "dh.pem")):
            VPNService.execute_easyrsa_command(tenant.pki_dir, "gen-dh")

        # will call run_playbook
        super(SyncVPNTenant, self).sync_fields(tenant, fields)

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
