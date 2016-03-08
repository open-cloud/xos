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
from plus import PlusSerializerMixin
from xos.apibase import XOSListCreateAPIView, XOSRetrieveUpdateDestroyAPIView, XOSPermissionDenied

if hasattr(serializers, "ReadOnlyField"):
    # rest_framework 3.x
    ReadOnlyField = serializers.ReadOnlyField
else:
    # rest_framework 2.x
    ReadOnlyField = serializers.Field

def get_default_vtr_service():
    vtr_services = VTRService.get_service_objects().all()
    if vtr_services:
        return vtr_services[0].id
    return None

class VTRTenantIdSerializer(serializers.ModelSerializer, PlusSerializerMixin):
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
            model = VTRTenant
            fields = ('humanReadableName', 'id', 'provider_service', 'target_id', 'scope', 'test', 'argument', 'result', 'result_code', 'is_synced', 'backend_status' )

        def getHumanReadableName(self, obj):
            return obj.__unicode__()

        def isSynced(self, obj):
            return (obj.enacted is not None) and (obj.enacted >= obj.updated)

class VTRTenantList(XOSListCreateAPIView):
    serializer_class = VTRTenantIdSerializer

    method_kind = "list"
    method_name = "truckroll"

    def get_queryset(self):
        queryset = VTRTenant.get_tenant_objects().select_related().all()

        test = self.request.QUERY_PARAMS.get('test', None)
        if test is not None:
            ids = [x.id for x in queryset if x.get_attribute("test", None)==test]
            queryset = queryset.filter(id__in=ids)

        return queryset

    def post(self, request, format=None):
        data = request.DATA

        existing_obj = None
#        for obj in VTRTenant.get_tenant_objects().all():
#            if (obj.tesst == data.get("test", None)) and (obj.target == data.get("target", None))):
#               existing_obj = obj

        if existing_obj:
            serializer = VTRTenantIdSerializer(existing_obj)
            headers = self.get_success_headers(serializer.data)
            return Response( serializer.data, status=status.HTTP_200_OK )

        return super(VTRTenantList, self).post(request, format)

class VTRTenantDetail(XOSRetrieveUpdateDestroyAPIView):
    serializer_class = VTRTenantIdSerializer
    queryset = VTRTenant.get_tenant_objects().select_related().all()

    method_kind = "detail"
    method_name = "truckroll"





