import os
import shutil
import sys

from django.db.models import F, Q

from services.openvpn.models import OpenVPNService, OpenVPNTenant
from synchronizers.base.SyncInstanceUsingAnsible import \
    SyncInstanceUsingAnsible

parentdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, parentdir)


class SyncOpenVPNTenant(SyncInstanceUsingAnsible):
    """Class for syncing a OpenVPNTenant using Ansible.

    This SyncStep creates any necessary files for the OpenVPNTenant using ESAY RSA and then runs the
    Ansible template to start the server on an instance.
    """
    provides = [OpenVPNTenant]
    observes = OpenVPNTenant
    requested_interval = 0
    template_name = "sync_openvpntenant.yaml"
    service_key_name = "/opt/xos/synchronizers/openvpn/openvpn_private_key"

    def fetch_pending(self, deleted):
        if (not deleted):
            objs = OpenVPNTenant.get_tenant_objects().filter(
                Q(enacted__lt=F('updated')) |
                Q(enacted=None), Q(lazy_blocked=False))
        else:
            objs = OpenVPNTenant.get_deleted_tenant_objects()

        return objs

    def get_extra_attributes(self, tenant):
        return {"is_persistent": tenant.is_persistent,
                "vpn_subnet": tenant.vpn_subnet,
                "server_network": tenant.server_network,
                "clients_can_see_each_other": (
                    tenant.clients_can_see_each_other),
                "port_number": tenant.port_number,
                "protocol": tenant.protocol,
                "pki_dir": OpenVPNService.get_pki_dir(tenant)
                }

    def sync_fields(self, o, fields):
        pki_dir = OpenVPNService.get_pki_dir(o)

        if (not os.path.isdir(pki_dir)):
            OpenVPNService.execute_easyrsa_command(pki_dir, "init-pki")
            OpenVPNService.execute_easyrsa_command(
                pki_dir, "--req-cn=XOS build-ca nopass")

        # Very hacky way to handle VPNs that need to share CAs
        if (o.use_ca_from_id):
            tenant = OpenVPNTenant.get_tenant_objects().filter(
                pk=o.use_ca_from_id)[0]
            other_pki_dir = OpenVPNService.get_pki_dir(tenant)
            shutil.copy2(other_pki_dir + "/ca.crt", pki_dir)
            shutil.copy2(other_pki_dir + "/private/ca.key",
                         pki_dir + "/private")

        # If the server has to be built then we need to build it
        if (not os.path.isfile(pki_dir + "/issued/server.crt")):
            OpenVPNService.execute_easyrsa_command(
                pki_dir, "build-server-full server nopass")
            OpenVPNService.execute_easyrsa_command(pki_dir, "gen-dh")

        # Get the most recent list of revoked clients
        OpenVPNService.execute_easyrsa_command(pki_dir, "gen-crl")

        # Super runs the playbook
        super(SyncOpenVPNTenant, self).sync_fields(o, fields)
