import os
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

    def __init__(self, *args, **kwargs):
        super(SyncVPNTenant, self).__init__(*args, **kwargs)

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

    def run_playbook(self, o, fields):
        # Generate the server files
        if (not os.path.isfile(o.pki_dir + "/issued/server.crt")):
            VPNService.execute_easyrsa_command(
                o.pki_dir, "build-server-full server nopass")
            VPNService.execute_easyrsa_command(o.pki_dir, "gen-crl")
        super(SyncVPNTenant, self).run_playbook(o, fields)
