from django.core.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from services.vpn.models import VPNTenant

class VpnTenantsList(APIView):
    method_kind = "list"
    method_name = "vpntenants"

    def get(self, request, format=None):
        if (not request.user.is_authenticated()):
            raise PermissionDenied("You must be authenticated in order to use this API")
        return Response(VPNTenant.get_tenant_objects())

class ClientScript(APIView):
    method_kind = "detail"
    method_name = "clientscript"

    def get(self, request, format=None):
        if (not request.user.is_authenticated()):
            raise PermissionDenied("You must be authenticated in order to use this API")
        return Response(VPNTenant.get_tenant_objects())
