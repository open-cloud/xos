import jinja2
from core.models import TenantPrivilege
from plus import PlusSerializerMixin
from rest_framework import serializers
from services.openvpn.models import OpenVPNService, OpenVPNTenant
from xos.apibase import XOSListCreateAPIView

if hasattr(serializers, "ReadOnlyField"):
    # rest_framework 3.x
    ReadOnlyField = serializers.ReadOnlyField
else:
    # rest_framework 2.x
    ReadOnlyField = serializers.Field


def get_default_openvpn_service():
    openvpn_services = OpenVPNService.get_service_objects().all()
    if openvpn_services:
        return openvpn_services[0].id
    return None


class OpenVPNTenantSerializer(serializers.ModelSerializer, PlusSerializerMixin):
    """A Serializer for the OpenVPNTenant that has the minimum information required for clients.

    Attributes:
        id (ReadOnlyField): The ID of OpenVPNTenant.
        server_network (ReadOnlyField): The network of the VPN.
        vpn_subnet (ReadOnlyField): The subnet of the VPN.
        script_text (SerializerMethodField): The text of the script for the client to use to
            connect.
    """
    id = ReadOnlyField()
    server_network = ReadOnlyField()
    vpn_subnet = ReadOnlyField()
    script_text = serializers.SerializerMethodField()

    class Meta:
        model = OpenVPNTenant
        fields = ('id', 'service_specific_attribute', 'vpn_subnet',
                  'server_network', 'script_text')

    def get_script_text(self, obj):
        """Gets the text of the client script for the requesting user.

        Parameters:
            obj (services.openvpn.models.OpenVPNTenant): The OpenVPNTenant to connect to.

        Returns:
            str: The client script as a str.
        """
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader("/opt/xos/services/openvpn/templates"))
        template = env.get_template("connect.vpn.j2")
        client_name = self.context['request'].user.email + "-" + str(obj.id)
        remote_ids = list(obj.failover_server_ids)
        remote_ids.insert(0, obj.id)
        remotes = OpenVPNTenant.get_tenant_objects().filter(pk__in=remote_ids)
        pki_dir = OpenVPNService.get_pki_dir(obj)
        fields = {"client_name": client_name,
                  "remotes": remotes,
                  "is_persistent": obj.is_persistent,
                  "ca_crt": obj.get_ca_crt(pki_dir),
                  "client_crt": obj.get_client_cert(client_name, pki_dir),
                  "client_key": obj.get_client_key(client_name, pki_dir)
                 }
        return template.render(fields)


class OpenVPNTenantList(XOSListCreateAPIView):
    """Class that provides a list of OpenVPNTenants that the user has permission to access."""
    serializer_class = OpenVPNTenantSerializer
    method_kind = "list"
    method_name = "openvpntenant"

    def get_queryset(self):
        # Get every privilege for this user
        tenants_privs = TenantPrivilege.objects.all().filter(
            user=self.request.user)
        vpn_tenants = []
        for priv in tenants_privs:
            vpn_tenants.append(
                OpenVPNTenant.get_tenant_objects().filter(pk=priv.tenant.pk)[0])
        return vpn_tenants
