from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework import status
from core.models import *
from django.forms import widgets
from services.cord.models import CordSubscriberRoot
from services.vtr.models import VTRTenant, VTRService
from xos.apibase import XOSListCreateAPIView, XOSRetrieveUpdateDestroyAPIView, XOSPermissionDenied
from api.xosapi_helpers import PlusModelSerializer, XOSViewSet, ReadOnlyField

def get_default_vtr_service():
    vtr_services = VTRService.get_service_objects().all()
    if vtr_services:
        return vtr_services[0]
    return None

class VTRTenantForAPI(VTRTenant):
    class Meta:
        proxy = True
        app_label = "cord"

class VTRTenantSerializer(PlusModelSerializer):
        id = ReadOnlyField()
        target_id = serializers.IntegerField()
        test = serializers.CharField()
        scope = serializers.CharField()
        argument = serializers.CharField(required=False)
        provider_service = serializers.PrimaryKeyRelatedField(queryset=VTRService.get_service_objects().all(), default=get_default_vtr_service)
        result = serializers.CharField(required=False)
        result_code = serializers.CharField(required=False)
        backend_status = ReadOnlyField()

        humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
        is_synced = serializers.SerializerMethodField("isSynced")

        class Meta:
            model = VTRTenantForAPI
            fields = ('humanReadableName', 'id', 'provider_service', 'target_id', 'scope', 'test', 'argument', 'result', 'result_code', 'is_synced', 'backend_status' )

        def getHumanReadableName(self, obj):
            return obj.__unicode__()

        def isSynced(self, obj):
            return (obj.enacted is not None) and (obj.enacted >= obj.updated)

class TruckRollViewSet(XOSViewSet):
    base_name = "truckroll"
    method_name = "truckroll"
    method_kind = "viewset"
    queryset = VTRTenantForAPI.get_tenant_objects().all() # select_related().all()
    serializer_class = VTRTenantSerializer

    @classmethod
    def get_urlpatterns(self, api_path="^"):
        patterns = super(TruckRollViewSet, self).get_urlpatterns(api_path=api_path)

        return patterns

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

