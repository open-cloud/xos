import os
import sys

from django.db.models import F, Q
from services.vpn.models import VPNTenant
from subprocess import Popen, PIPE
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
        return {"is_persistent": tenant.is_persistent,
                "vpn_subnet": tenant.vpn_subnet,
                "server_network": tenant.server_network,
                "clients_can_see_each_other": tenant.clients_can_see_each_other,
                "tenant_id": tenant.id
                }

    def run_playbook(self, o, fields):
        # Generate the server files
        (stdout, stderr) = Popen("/opt/openvpn/easyrsa3/easyrsa --batch build-server-full server-" + o.id + " nopass",shell=True, stdout=PIPE).communicate()
        print(str(stdout))
        print(str(stderr))
        super(SyncVPNTenant, self).run_playbook(o, fields)
