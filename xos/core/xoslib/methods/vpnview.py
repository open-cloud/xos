from rest_framework.response import Response
from rest_framework.views import APIView
from services.vpn.models import VPNTenant

class VpnTenantsList(APIView):
    method_kind = "list"
    method_name = "vpntenants"

    def get(self, request, format=None):
        return Response(VPNTenant.get_tenant_objects())
