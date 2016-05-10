from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework import status
from core.models import *
from django.forms import widgets
from xos.apibase import XOSListCreateAPIView, XOSRetrieveUpdateDestroyAPIView, XOSPermissionDenied
from api.xosapi_helpers import PlusModelSerializer, XOSViewSet, ReadOnlyField

from services.ceilometer.models import MonitoringChannel, CeilometerService

def get_default_ceilometer_service():
    ceilometer_services = CeilometerService.get_service_objects().all()
    if ceilometer_services:
        return ceilometer_services[0].id
    return None

class MonitoringChannelForAPI(MonitoringChannel):
    class Meta:
        proxy = True
        app_label = "ceilometer"

    @property
    def related(self):
        related = {}
        if self.creator:
            related["creator"] = self.creator.username
        if self.instance:
            related["instance_id"] = self.instance.id
            related["instance_name"] = self.instance.name
            if self.instance.node:
                related["compute_node_name"] = self.instance.node.name
        return related

class MonitoringChannelSerializer(PlusModelSerializer):
        id = ReadOnlyField()
        service_specific_attribute = ReadOnlyField()
        ceilometer_url = ReadOnlyField()
        tenant_list_str = ReadOnlyField()
        #creator = ReadOnlyField()
        #instance = ReadOnlyField()
        provider_service = serializers.PrimaryKeyRelatedField(queryset=CeilometerService.get_service_objects().all(), default=get_default_ceilometer_service)

        humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
        related = serializers.DictField(required=False)

        #computeNodeName = serializers.SerializerMethodField("getComputeNodeName")

        class Meta:
            model = MonitoringChannelForAPI
            fields = ('humanReadableName', 'id', 'provider_service', 'service_specific_attribute', 'ceilometer_url', 'tenant_list_str', 'related' )

        def getHumanReadableName(self, obj):
            return obj.__unicode__()

        #def getComputeNodeName(self, obj):
        #    instance = obj.instance
        #    if not instance:
        #        return None
        #    return instance.node.name

class MonitoringChannelSet(XOSViewSet):
    base_name = "monitoringchannel"
    method_name = "monitoringchannel"
    method_kind = "viewset"
    queryset = MonitoringChannelForAPI.get_tenant_objects().all()
    serializer_class = MonitoringChannelSerializer

    def get_queryset(self):
        queryset = MonitoringChannelForAPI.get_tenant_objects().all()

        current_user = self.request.user.username
        if current_user is not None:
            ids = [x.id for x in queryset if x.creator.username==current_user]
            queryset = queryset.filter(id__in=ids)

        return queryset

    def create(self, request):
        current_user = request.user.username
        existing_obj = None
        for obj in MonitoringChannelForAPI.get_tenant_objects().all():
            if (obj.creator.username == current_user):
               existing_obj = obj
               break

        if existing_obj:
            serializer = MonitoringChannelSerializer(existing_obj)
            headers = self.get_success_headers(serializer.data)
            return Response( serializer.data, status=status.HTTP_200_OK )

        return super(MonitoringChannelSet, self).create(request)
