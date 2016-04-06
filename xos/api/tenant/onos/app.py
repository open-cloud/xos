from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework import status
from core.models import *
from django.forms import widgets
from services.onos.models import ONOSService, ONOSApp
from xos.apibase import XOSListCreateAPIView, XOSRetrieveUpdateDestroyAPIView, XOSPermissionDenied
from api.xosapi_helpers import PlusModelSerializer, XOSViewSet, ReadOnlyField

def get_default_onos_service():
    onos_services = ONOSService.get_service_objects().all()
    if onos_services:
        return onos_services[0].id
    return None

class ONOSAppSerializer(PlusModelSerializer):
    id = ReadOnlyField()
    name = serializers.CharField()
    dependencies = serializers.CharField()

    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    class Meta:
        model = ONOSApp
        fields = ('humanReadableName', 'id', 'name', 'dependencies')

    def getHumanReadableName(self, obj):
        return obj.__unicode__()

class TenantAttributeSerializer(serializers.Serializer):
    id = ReadOnlyField()
    name = serializers.CharField()
    value = serializers.CharField()

class ONOSAppViewSet(XOSViewSet):
    base_name = "app"
    method_name = "app"
    method_kind = "viewset"
    queryset = ONOSApp.get_tenant_objects().all()
    serializer_class = ONOSAppSerializer

    def get_serializer_class(self):
        if self.action == "set_attribute":
            return TenantAttributeSerializer
        else:
            return super(ONOSAppViewSet, self).get_serializer_class()

    @classmethod
    def get_urlpatterns(self, api_path="^"):
        patterns = super(ONOSAppViewSet, self).get_urlpatterns(api_path=api_path)

        patterns.append( self.detail_url("attributes/$", {"get": "get_attributes", "post": "add_attribute"}, "attributes") )
        patterns.append( self.detail_url("attributes/(?P<attribute>[0-9]+)/$", {"get": "get_attribute", "put": "set_attribute"}, "attribute") )

        return patterns

    def get_attributes(self, request, pk=None):
        subscriber = self.get_object()
        return Response(TenantAttributeSerializer(subscriber.tenantattributes.all(), many=True).data)

    def add_attribute(self, request, pk=None):
        pass

    def get_attribute(self, request, pk=None, attribute=None):
        subscriber = self.get_object()
        att = TenantAttribute.objects.get(pk=attribute)
        return Response(TenantAttributeSerializer(att).data)

    def set_attribute(self, request, pk=None, attribute=None):
        subscriber = self.get_object()
        att = TenantAttribute.objects.get(pk=attribute)
        ser = TenantAttributeSerializer(att, data=request.data)
        ser.is_valid(raise_exception = True)
        return Response(TenantAttributeSerializer(attribute).data)






