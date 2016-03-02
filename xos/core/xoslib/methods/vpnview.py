from django.core.exceptions import PermissionDenied
from plus import PlusSerializerMixin
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from services.vpn.models import VPNService, VPNTenant
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
        creator = ReadOnlyField()
        instance = ReadOnlyField()
        provider_service = serializers.PrimaryKeyRelatedField(queryset=VPNService.get_service_objects().all(), default=get_default_vpn_service)

        humanReadableName = serializers.SerializerMethodField("getHumanReadableName")

        computeNodeName = serializers.SerializerMethodField("getComputeNodeName")

        class Meta:
            model = VPNTenant
            fields = ('humanReadableName', 'id', 'provider_service',
                      'service_specific_attribute', 'vpn_subnet',
                      'server_network', 'creator', 'instance',
                      'computeNodeName', 'is_persistent', 'clients_can_see_each_other',
                      'ca_crt', 'port_number')

        def getHumanReadableName(self, obj):
            return obj.__unicode__()

        def getComputeNodeName(self, obj):
            instance = obj.instance
            if not instance:
                return None
            return instance.node.name

class VPNTenantList(XOSListCreateAPIView):
    serializer_class = VPNTenantSerializer
    queryset = VPNTenant.get_tenant_objects().all()
    method_kind = "list"
    method_name = "vpntenant"


class ClientScript(APIView):
    method_kind = "detail"
    method_name = "clientscript"

    def get(self, request, format=None):
        if (not request.user.is_authenticated()):
            raise PermissionDenied("You must be authenticated in order to use this API")
        tenantId = request.QUERY_PARAMS.get('tenantId', None)
        serializer = VPNTenantSerializer(VPNTenant.get_tenant_objects().filter(id=tenantId)[0])
        return Response(serializer.data, status=HTTP_200_OK)
