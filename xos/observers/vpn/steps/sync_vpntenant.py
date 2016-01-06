import os
import sys
from django.db.models import Q, F
from observers.base.SyncInstanceUsingAnsible import SyncInstanceUsingAnsible
from services.vpn.models import VPNTenant

parentdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, parentdir)

class SyncVPNTenant(SyncInstanceUsingAnsible):
    provides = [VPNTenant]
    observes = VPNTenant
    requested_interval = 0
    template_name = "sync_vpntenant.yaml"
    service_key_name = "/opt/xos/observers/vpn/vpn_private_key"

    def __init__(self, *args, **kwargs):
        super(SyncVPNTenant, self).__init__(*args, **kwargs)

    def fetch_pending(self, deleted):
        if (not deleted):
            objs = VPNTenant.get_tenant_objects().filter(
                Q(enacted__lt=F('updated')) | Q(enacted=None), Q(lazy_blocked=False))
            for tenant in objs:
                tenant.client_conf = generate_client_conf(tenant)
        else:
            objs = VPNTenant.get_deleted_tenant_objects()

        return objs

    def get_extra_attributes(self, o):
        return {"server_key": o.server_key.splitlines()}

    def generate_client_conf(self, tenant):
        conf = "remote " + tenant.nat_ip + "\n"
        conf += "dev tun\n"
        conf += "ifconfig " + tenant.client_address + " " + tenant.server_address + "\n"
        conf += "secret static.key\n"
        conf += "keepalive 10 60\n"
        conf += "ping-timer-rem\n"
        conf += "persist-tun\n"
        conf += "persist-key"
        return conf
