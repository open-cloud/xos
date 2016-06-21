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
    name = serializers.CharField(required=False)
    value = serializers.CharField(required=False)

class ONOSAppViewSet(XOSViewSet):
    base_name = "app"
    method_name = "app"
    method_kind = "viewset"
    queryset = ONOSApp.get_tenant_objects().all()
    serializer_class = ONOSAppSerializer

    custom_serializers = {"set_attribute": TenantAttributeSerializer}

    @classmethod
    def get_urlpatterns(self, api_path="^"):
        patterns = super(ONOSAppViewSet, self).get_urlpatterns(api_path=api_path)

        patterns.append( self.detail_url("attributes/$", {"get": "get_attributes", "post": "add_attribute"}, "attributes") )
        patterns.append( self.detail_url("attributes/(?P<attribute>[0-9]+)/$", {"get": "get_attribute", "put": "set_attribute", "delete": "delete_attribute"}, "attribute") )

        return patterns

    def get_attributes(self, request, pk=None):
        app = self.get_object()
        return Response(TenantAttributeSerializer(app.tenantattributes.all(), many=True).data)

    def add_attribute(self, request, pk=None):
        app = self.get_object()
        ser = TenantAttributeSerializer(data=request.data)
        ser.is_valid(raise_exception = True)
        att = TenantAttribute(tenant=app, **ser.validated_data)
        att.save()
        return Response(TenantAttributeSerializer(att).data)

    def get_attribute(self, request, pk=None, attribute=None):
        app = self.get_object()
        att = TenantAttribute.objects.get(pk=attribute)
        return Response(TenantAttributeSerializer(att).data)

    def set_attribute(self, request, pk=None, attribute=None):
        app = self.get_object()
        att = TenantAttribute.objects.get(pk=attribute)
        ser = TenantAttributeSerializer(att, data=request.data)
        ser.is_valid(raise_exception = True)
        att.name = ser.validated_data.get("name", att.name)
        att.value = ser.validated_data.get("value", att.value)
        att.save()
        return Response(TenantAttributeSerializer(att).data)

    def delete_attribute(self, request, pk=None, attribute=None):
        att = TenantAttribute.objects.get(pk=attribute)
        att.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)






