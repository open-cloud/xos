from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework import status
from core.models import *
from django.forms import widgets
from services.cord.models import VSGTenant, VSGService, CordSubscriberRoot
from xos.apibase import XOSListCreateAPIView, XOSRetrieveUpdateDestroyAPIView, XOSPermissionDenied
from api.xosapi_helpers import PlusModelSerializer, XOSViewSet, ReadOnlyField

def get_default_vsg_service():
    vsg_services = VSGService.get_service_objects().all()
    if vsg_services:
        return vsg_services[0].id
    return None

class VSGTenantForAPI(VSGTenant):
    class Meta:
        proxy = True
        app_label = "cord"

    @property
    def related(self):
        related = {}
        if self.instance:
            related["instance_id"] = self.instance.id
        return related

class VSGTenantSerializer(PlusModelSerializer):
    id = ReadOnlyField()
    wan_container_ip = serializers.CharField()
    wan_container_mac = ReadOnlyField()
    related = serializers.DictField(required=False)

    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    class Meta:
        model = VSGTenantForAPI
        fields = ('humanReadableName', 'id', 'wan_container_ip', 'wan_container_mac', 'related' )

    def getHumanReadableName(self, obj):
        return obj.__unicode__()

class VSGTenantViewSet(XOSViewSet):
    base_name = "vsg"
    method_name = "vsg"
    method_kind = "viewset"
    queryset = VSGTenantForAPI.get_tenant_objects().all()
    serializer_class = VSGTenantSerializer

    @classmethod
    def get_urlpatterns(self, api_path="^"):
        patterns = super(VSGTenantViewSet, self).get_urlpatterns(api_path=api_path)

        return patterns






