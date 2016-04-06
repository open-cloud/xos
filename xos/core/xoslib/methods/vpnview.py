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
        script_text = ReadOnlyField()
        provider_service = serializers.PrimaryKeyRelatedField(
            queryset=VPNService.get_service_objects().all(),
            default=get_default_vpn_service)

        humanReadableName = serializers.SerializerMethodField(
                "getHumanReadableName")

        computeNodeName = serializers.SerializerMethodField(
                "getComputeNodeName")

        class Meta:
            model = VPNTenant
            fields = ('humanReadableName', 'id', 'provider_service',
                      'service_specific_attribute', 'vpn_subnet',
                      'server_network', 'creator', 'instance', 'protocol',
                      'computeNodeName', 'is_persistent',
                      'clients_can_see_each_other', 'ca_crt', 'port_number',
                      'script_text', 'failover_servers')

        def getHumanReadableName(self, obj):
            return obj.__unicode__()

        def getComputeNodeName(self, obj):
            instance = obj.instance
            if not instance:
                return None
            return instance.node.name


class VPNTenantList(XOSListCreateAPIView):
    serializer_class = VPNTenantSerializer
    method_kind = "list"
    method_name = "vpntenant"

    def get_queryset(self):
        # Get every privilege for this user
        queryset = TenantPrivlege.objects.all().filter(user=self.request.user)
        queryset = [
            priv.tenant for priv in queryset if priv.tenant.KIND == VPN_KIND]
        for tenant in queryset:
            tenant.script_text = (
                tenant.create_client_script(
                    self.request.user.email + "-" + str(tenant.id)))
        return queryset
