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
        service_specific_attribute = ReadOnlyField()
        server_network = ReadOnlyField()
        vpn_subnet = ReadOnlyField()
        is_persistent = ReadOnlyField()
        clients_can_see_each_other = ReadOnlyField()
        ca_crt = ReadOnlyField()
        port_number = ReadOnlyField()
        protocol = ReadOnlyField()
        failover_servers = ReadOnlyField()
        creator = ReadOnlyField()
        instance = ReadOnlyField()
        use_ca_from = ReadOnlyField()
        provider_service = serializers.PrimaryKeyRelatedField(
            queryset=VPNService.get_service_objects().all(),
            default=get_default_vpn_service)
        script_text = serializers.SerializerMethodField(
                "get_script_text")

        class Meta:
            model = VPNTenant
            fields = ('id', 'provider_service', 'use_ca_from',
                      'service_specific_attribute', 'vpn_subnet',
                      'server_network', 'creator', 'instance', 'protocol',
                      'is_persistent',
                      'clients_can_see_each_other', 'ca_crt', 'port_number',
                      'script_text', 'failover_servers')

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
