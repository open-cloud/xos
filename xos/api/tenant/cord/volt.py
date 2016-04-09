from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework import status
from core.models import *
from django.forms import widgets
from services.cord.models import VOLTTenant, VOLTService, CordSubscriberRoot
from xos.apibase import XOSListCreateAPIView, XOSRetrieveUpdateDestroyAPIView, XOSPermissionDenied
from api.xosapi_helpers import PlusModelSerializer, XOSViewSet, ReadOnlyField

def get_default_volt_service():
    volt_services = VOLTService.get_service_objects().all()
    if volt_services:
        return volt_services[0].id
    return None

class VOLTTenantForAPI(VOLTTenant):
    class Meta:
        proxy = True
        app_label = "cord"

    @property
    def subscriber(self):
        return self.subscriber_root.id

    @subscriber.setter
    def subscriber(self, value):
        self.subscriber_root = value # CordSubscriberRoot.get_tenant_objects().get(id=value)

    @property
    def related(self):
        related = {}
        if self.vcpe:
            related["vsg_id"] = self.vcpe.id
            if self.vcpe.instance:
                related["instance_id"] = self.vcpe.instance.id
                related["instance_name"] = self.vcpe.instance.name
                related["wan_container_ip"] = self.vcpe.wan_container_ip
                if self.vcpe.instance.node:
                    related["compute_node_name"] = self.vcpe.instance.node.name
        return related

class VOLTTenantSerializer(PlusModelSerializer):
    id = ReadOnlyField()
    service_specific_id = serializers.CharField(required=False)
    s_tag = serializers.CharField()
    c_tag = serializers.CharField()
    subscriber = serializers.PrimaryKeyRelatedField(queryset=CordSubscriberRoot.get_tenant_objects().all(), required=False)
    related = serializers.DictField(required=False)

    property_fields=["subscriber"]

    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    class Meta:
        model = VOLTTenantForAPI
        fields = ('humanReadableName', 'id', 'service_specific_id', 's_tag', 'c_tag', 'subscriber', 'related' )

    def getHumanReadableName(self, obj):
        return obj.__unicode__()

class VOLTTenantViewSet(XOSViewSet):
    base_name = "volt"
    method_name = "volt"
    method_kind = "viewset"
    queryset = VOLTTenantForAPI.get_tenant_objects().all() # select_related().all()
    serializer_class = VOLTTenantSerializer

    @classmethod
    def get_urlpatterns(self, api_path="^"):
        patterns = super(VOLTTenantViewSet, self).get_urlpatterns(api_path=api_path)

        return patterns

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        c_tag = self.request.query_params.get('c_tag', None)
        if c_tag is not None:
            ids = [x.id for x in queryset if x.get_attribute("c_tag", None)==c_tag]
            queryset = queryset.filter(id__in=ids)

        s_tag = self.request.query_params.get('s_tag', None)
        if s_tag is not None:
            ids = [x.id for x in queryset if x.get_attribute("s_tag", None)==s_tag]
            queryset = queryset.filter(id__in=ids)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)





