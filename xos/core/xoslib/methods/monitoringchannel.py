from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework import status
from core.models import *
from django.forms import widgets
from services.ceilometer.models import MonitoringChannel, CeilometerService
from plus import PlusSerializerMixin
from xos.apibase import XOSListCreateAPIView, XOSRetrieveUpdateDestroyAPIView, XOSPermissionDenied

if hasattr(serializers, "ReadOnlyField"):
    # rest_framework 3.x
    ReadOnlyField = serializers.ReadOnlyField
else:
    # rest_framework 2.x
    ReadOnlyField = serializers.Field

def get_default_ceilometer_service():
    ceilometer_services = CeilometerService.get_service_objects().all()
    if ceilometer_services:
        return ceilometer_services[0].id
    return None

class MonitoringChannelSerializer(serializers.ModelSerializer, PlusSerializerMixin):
        id = ReadOnlyField()
        service_specific_attribute = ReadOnlyField()
        ceilometer_url = ReadOnlyField()
        tenant_list_str = ReadOnlyField()
        creator = ReadOnlyField()
        instance = ReadOnlyField()
        provider_service = serializers.PrimaryKeyRelatedField(queryset=CeilometerService.get_service_objects().all(), default=get_default_ceilometer_service)

        humanReadableName = serializers.SerializerMethodField("getHumanReadableName")

        computeNodeName = serializers.SerializerMethodField("getComputeNodeName")

        class Meta:
            model = MonitoringChannel
            fields = ('humanReadableName', 'id', 'provider_service', 'service_specific_attribute', 'ceilometer_url', 'tenant_list_str', 'creator', 'instance', 'computeNodeName' )

        def getHumanReadableName(self, obj):
            return obj.__unicode__()

        def getComputeNodeName(self, obj):
            instance = obj.instance
            if not instance:
                return None
            return instance.node.name

class MonitoringChannelList(XOSListCreateAPIView):
    serializer_class = MonitoringChannelSerializer

    method_kind = "list"
    method_name = "monitoringchannel"

    def get_queryset(self):
        queryset = MonitoringChannel.get_tenant_objects().select_related().all()

        current_user = self.request.user.username
        if current_user is not None:
            ids = [x.id for x in queryset if x.creator.username==current_user]
            queryset = queryset.filter(id__in=ids)

        return queryset

    def post(self, request, format=None):
        current_user = request.user.username
        existing_obj = None
        for obj in MonitoringChannel.get_tenant_objects().all():
            if (obj.creator.username == current_user):
               existing_obj = obj
               break

        if existing_obj:
            serializer = MonitoringChannelSerializer(existing_obj)
            headers = self.get_success_headers(serializer.data)
            return Response( serializer.data, status=status.HTTP_200_OK )

        return super(MonitoringChannelList, self).post(request, format)

class MonitoringChannelDetail(XOSRetrieveUpdateDestroyAPIView):
    serializer_class = MonitoringChannelSerializer
    queryset = MonitoringChannel.get_tenant_objects().select_related().all()

    method_kind = "detail"
    method_name = "monitoringchannel"

