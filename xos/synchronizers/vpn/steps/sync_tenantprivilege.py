import os
import sys

from core.models import TenantPrivilege
from services.vpn.models import VPN_KIND, VPNService, VPNTenant
from synchronizers.base.syncstep import DeferredException, SyncStep

parentdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, parentdir)


class SyncTenantPrivilege(SyncStep):
    """Class for syncing a TenantPrivilege."""
    provides = [TenantPrivilege]
    observes = TenantPrivilege
    requested_interval = 0

    def fetch_pending(self, deleted):
        privs = super(SyncTenantPrivilege, self).fetch_pending(deleted)
        # Get only the TenantPrivileges that relate to VPNTenants
        privs = [priv for priv in privs if priv.tenant.kind == VPN_KIND]
        return privs

    def sync_record(self, record):
        if (not record.tenant.id):
            raise DeferredException("Privilege waiting on VPN Tenant ID")
        certificate = self.get_certificate_name(record)
        tenant = VPNTenant.get_tenant_objects().filter(pk=record.tenant.id)[0]
        if (not tenant):
            raise DeferredException("Privilege waiting on VPN Tenant")
        # Only add a certificate if ones does not yet exist
        pki_dir = VPNService.get_pki_dir(tenant)
        if (not os.path.isfile(pki_dir + "/issued/" + certificate + ".crt")):
            VPNService.execute_easyrsa_command(
                pki_dir, "build-client-full " + certificate + " nopass")
            tenant.save()
        record.save()

    def delete_record(self, record):
        if (not record.tenant.id):
            return
        certificate = self.get_certificate_name(record)
        tenant = VPNTenant.get_tenant_objects().filter(pk=record.tenant.id)[0]
        if (not tenant):
            return
        # If the client has already been reovked don't do it again
        pki_dir = VPNService.get_pki_dir(tenant)
        if (os.path.isfile(pki_dir + "/issued/" + certificate + ".crt")):
            VPNService.execute_easyrsa_command(
                pki_dir, "revoke " + certificate)
            # Revoking a client cert does not delete any of the files
            # to make sure that we can add this user again we need to
            # delete all of the files created by easyrsa
            os.remove(pki_dir + "/issued/" + certificate + ".crt")
            os.remove(pki_dir + "/private/" + certificate + ".key")
            os.remove(pki_dir + "/reqs/" + certificate + ".req")
            tenant.save()

        record.delete()

    def get_certificate_name(self, tenant_privilege):
        return (str(tenant_privilege.user.email) +
                "-" + str(tenant_privilege.tenant.id))
