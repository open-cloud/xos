import os
import sys

from core.models import TenantPrivilege
from services.openvpn.models import OPENVPN_KIND, OpenVPNService, OpenVPNTenant
from synchronizers.base.syncstep import DeferredException, SyncStep

parentdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, parentdir)


class SyncTenantPrivilege(SyncStep):
    """Class for syncing a TenantPrivilege for a OpenVPNTenant.

    This SyncStep isolates the updated TenantPrivileges that are for OpenVPNTenants and performs
    actions if the TenantPrivilege has been added or deleted. For added privileges a new client
    certificate and key are made, signed with the ca.crt file used by this OpenVPNTenant. For deleted
    privileges the client certificate is revoked and the files associated are deleted. In both
    cases the associated OpenVPNTenant is saved causing the OpenVPNTenant synchronizer to run.
    """
    provides = [TenantPrivilege]
    observes = TenantPrivilege
    requested_interval = 0

    def fetch_pending(self, deleted):
        privs = super(SyncTenantPrivilege, self).fetch_pending(deleted)
        # Get only the TenantPrivileges that relate to OpenVPNTenants
        privs = [priv for priv in privs if priv.tenant.kind == OPENVPN_KIND]
        return privs

    def sync_record(self, record):
        if (not record.tenant.id):
            raise DeferredException("Privilege waiting on VPN Tenant ID")
        certificate = self.get_certificate_name(record)
        tenant = OpenVPNTenant.get_tenant_objects().filter(pk=record.tenant.id)[0]
        if (not tenant):
            raise DeferredException("Privilege waiting on VPN Tenant")
        # Only add a certificate if ones does not yet exist
        pki_dir = OpenVPNService.get_pki_dir(tenant)
        if (not os.path.isfile(pki_dir + "/issued/" + certificate + ".crt")):
            OpenVPNService.execute_easyrsa_command(
                pki_dir, "build-client-full " + certificate + " nopass")
            tenant.save()
        record.save()

    def delete_record(self, record):
        if (not record.tenant.id):
            return
        certificate = self.get_certificate_name(record)
        tenant = OpenVPNTenant.get_tenant_objects().filter(pk=record.tenant.id)[0]
        if (not tenant):
            return
        # If the client has already been reovked don't do it again
        pki_dir = OpenVPNService.get_pki_dir(tenant)
        if (os.path.isfile(pki_dir + "/issued/" + certificate + ".crt")):
            OpenVPNService.execute_easyrsa_command(
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
        """Gets the name of a certificate for the given TenantPrivilege

        Parameters:
            tenant_privilege (core.models.TenantPrivilege): The TenantPrivilege to use to generate
                the certificate name.

        Returns:
            str: The certificate name.
        """
        return (str(tenant_privilege.user.email) +
                "-" + str(tenant_privilege.tenant.id))
