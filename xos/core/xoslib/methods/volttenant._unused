from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework import status
from core.models import *
from django.forms import widgets
from services.volt.models import VOLTTenant, VOLTService, CordSubscriberRoot
from plus import PlusSerializerMixin
from xos.apibase import XOSListCreateAPIView, XOSRetrieveUpdateDestroyAPIView, XOSPermissionDenied

if hasattr(serializers, "ReadOnlyField"):
    # rest_framework 3.x
    ReadOnlyField = serializers.ReadOnlyField
else:
    # rest_framework 2.x
    ReadOnlyField = serializers.Field

def get_default_volt_service():
    volt_services = VOLTService.get_service_objects().all()
    if volt_services:
        return volt_services[0].id
    return None

class VOLTTenantIdSerializer(serializers.ModelSerializer, PlusSerializerMixin):
        id = ReadOnlyField()
        service_specific_id = serializers.CharField()
        s_tag = serializers.CharField()
        c_tag = serializers.CharField()
        provider_service = serializers.PrimaryKeyRelatedField(queryset=VOLTService.get_service_objects().all(), default=get_default_volt_service)
        subscriber_root = serializers.PrimaryKeyRelatedField(queryset=CordSubscriberRoot.get_tenant_objects().all(), required=False)

        humanReadableName = serializers.SerializerMethodField("getHumanReadableName")

        computeNodeName = serializers.SerializerMethodField("getComputeNodeName")

        class Meta:
            model = VOLTTenant
            fields = ('humanReadableName', 'id', 'provider_service', 'service_specific_id', 's_tag', 'c_tag', 'computeNodeName', 'subscriber_root' )

        def getHumanReadableName(self, obj):
            return obj.__unicode__()

        def getComputeNodeName(self, obj):
            vcpe = obj.vcpe
            if not vcpe:
                return None
            instance = vcpe.instance
            if not instance:
                return None
            return instance.node.name

class VOLTTenantList(XOSListCreateAPIView):
    serializer_class = VOLTTenantIdSerializer

    method_kind = "list"
    method_name = "volttenant"

    def get_queryset(self):
        queryset = VOLTTenant.get_tenant_objects().select_related().all()

        service_specific_id = self.request.query_params.get('service_specific_id', None)
        if service_specific_id is not None:
            queryset = queryset.filter(service_specific_id=service_specific_id)

        c_tag = self.request.query_params.get('c_tag', None)
        if c_tag is not None:
            ids = [x.id for x in queryset if x.get_attribute("c_tag", None)==c_tag]
            queryset = queryset.filter(id__in=ids)

        s_tag = self.request.query_params.get('s_tag', None)
        if s_tag is not None:
            ids = [x.id for x in queryset if x.get_attribute("s_tag", None)==s_tag]
            queryset = queryset.filter(id__in=ids)

        return queryset

    def post(self, request, format=None):
        data = request.DATA

        existing_obj = None
        for obj in VOLTTenant.get_tenant_objects().all():
            if (obj.c_tag == data.get("c_tag", None)) and (obj.s_tag == data.get("s_tag", None)) and  (obj.service_specific_id == data.get("service_specific_id",None)):
               existing_obj = obj

        if existing_obj:
            serializer = VOLTTenantIdSerializer(existing_obj)
            headers = self.get_success_headers(serializer.data)
            return Response( serializer.data, status=status.HTTP_200_OK )

        return super(VOLTTenantList, self).post(request, format)

class VOLTTenantDetail(XOSRetrieveUpdateDestroyAPIView):
    serializer_class = VOLTTenantIdSerializer
    queryset = VOLTTenant.get_tenant_objects().select_related().all()

    method_kind = "detail"
    method_name = "volttenant"





