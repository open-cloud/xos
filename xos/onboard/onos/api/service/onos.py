from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework import status
from core.models import *
from django.forms import widgets
from services.onos.models import ONOSService
from xos.apibase import XOSListCreateAPIView, XOSRetrieveUpdateDestroyAPIView, XOSPermissionDenied
from api.xosapi_helpers import PlusModelSerializer, XOSViewSet, ReadOnlyField

class ONOSServiceSerializer(PlusModelSerializer):
    id = ReadOnlyField()
    rest_hostname = serializers.CharField(required=False)
    rest_port = serializers.CharField(default="8181")
    no_container = serializers.BooleanField(default=False)
    node_key = serializers.CharField(required=False)

    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    class Meta:
        model = ONOSService
        fields = ('humanReadableName', 'id', 'rest_hostname', 'rest_port', 'no_container', 'node_key')

    def getHumanReadableName(self, obj):
        return obj.__unicode__()

class ServiceAttributeSerializer(serializers.Serializer):
    id = ReadOnlyField()
    name = serializers.CharField(required=False)
    value = serializers.CharField(required=False)

class ONOSServiceViewSet(XOSViewSet):
    base_name = "onos"
    method_name = "onos"
    method_kind = "viewset"
    queryset = ONOSService.get_service_objects().all()
    serializer_class = ONOSServiceSerializer

    custom_serializers = {"set_attribute": ServiceAttributeSerializer}

    @classmethod
    def get_urlpatterns(self, api_path="^"):
        patterns = super(ONOSServiceViewSet, self).get_urlpatterns(api_path=api_path)

        patterns.append( self.detail_url("attributes/$", {"get": "get_attributes", "post": "add_attribute"}, "attributes") )
        patterns.append( self.detail_url("attributes/(?P<attribute>[0-9]+)/$", {"get": "get_attribute", "put": "set_attribute", "delete": "delete_attribute"}, "attribute") )

        return patterns

    def get_attributes(self, request, pk=None):
        svc = self.get_object()
        return Response(ServiceAttributeSerializer(svc.serviceattributes.all(), many=True).data)

    def add_attribute(self, request, pk=None):
        svc = self.get_object()
        ser = ServiceAttributeSerializer(data=request.data)
        ser.is_valid(raise_exception = True)
        att = ServiceAttribute(service=svc, **ser.validated_data)
        att.save()
        return Response(ServiceAttributeSerializer(att).data)

    def get_attribute(self, request, pk=None, attribute=None):
        svc = self.get_object()
        att = ServiceAttribute.objects.get(pk=attribute)
        return Response(ServiceAttributeSerializer(att).data)

    def set_attribute(self, request, pk=None, attribute=None):
        svc = self.get_object()
        att = ServiceAttribute.objects.get(pk=attribute)
        ser = ServicettributeSerializer(att, data=request.data)
        ser.is_valid(raise_exception = True)
        att.name = ser.validated_data.get("name", att.name)
        att.value = ser.validated_data.get("value", att.value)
        att.save()
        return Response(ServiceAttributeSerializer(att).data)

    def delete_attribute(self, request, pk=None, attribute=None):
        att = ServiceAttribute.objects.get(pk=attribute)
        att.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)






