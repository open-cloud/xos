from rest_framework.response import Response
from rest_framework.views import APIView

class VpnTenantsList(APIView):
    method_kind = "list"
    method_name = "vpntenants"

    def get(self, request, format=None):
        return Response(list())
