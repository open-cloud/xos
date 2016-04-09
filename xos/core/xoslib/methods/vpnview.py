from core.models import TenantPrivilege
from plus import PlusSerializerMixin
from rest_framework import serializers
from services.vpn.models import VPNService, VPNTenant, VPN_KIND
from xos.apibase import XOSListCreateAPIView

if hasattr(serializers, "ReadOnlyField"):
    # rest_framework 3.x
    ReadOnlyField = serializers.ReadOnlyField
else:
    # rest_framework 2.x
    ReadOnlyField = serializers.Field


def get_default_vpn_service():
    vpn_services = VPNService.get_service_objects().all()
    if vpn_services:
        return vpn_services[0].id
    return None


class VPNTenantSerializer(serializers.ModelSerializer, PlusSerializerMixin):
        id = ReadOnlyField()
        server_network = ReadOnlyField()
        vpn_subnet = ReadOnlyField()
        script_text = serializers.SerializerMethodField()

        class Meta:
            model = VPNTenant
            fields = ('id', 'service_specific_attribute', 'vpn_subnet',
                      'server_network', 'script_text')

        def get_script_text(self, obj):
            return obj.create_client_script(
                self.context['request'].user.email + "-" + str(obj.id))


class VPNTenantList(XOSListCreateAPIView):
    serializer_class = VPNTenantSerializer
    method_kind = "list"
    method_name = "vpntenant"

    def get_queryset(self):
        # Get every privilege for this user
        tenants_privs = TenantPrivilege.objects.all().filter(
            user=self.request.user)
        vpn_tenants = []
        for priv in tenants_privs:
            vpn_tenants.append(
                VPNTenant.get_tenant_objects().filter(pk=priv.tenant.pk)[0])
        return vpn_tenants
