from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework import status
from core.models import *
from django.forms import widgets
from services.cord.models import CordSubscriberRoot
from xos.apibase import XOSListCreateAPIView, XOSRetrieveUpdateDestroyAPIView, XOSPermissionDenied
from api.xosapi_helpers import PlusModelSerializer, XOSViewSet, ReadOnlyField

from services.exampleservice.models import ExampleTenant, ExampleService

def get_default_example_service():
    example_services = ExampleService.get_service_objects().all()
    if example_services:
        return example_services[0]
    return None

class ExampleTenantSerializer(PlusModelSerializer):
        id = ReadOnlyField()
        provider_service = serializers.PrimaryKeyRelatedField(queryset=ExampleService.get_service_objects().all(), default=get_default_example_service)
        tenant_message = serializers.CharField(required=False)
        backend_status = ReadOnlyField()

        humanReadableName = serializers.SerializerMethodField("getHumanReadableName")

        class Meta:
            model = ExampleTenant
            fields = ('humanReadableName', 'id', 'provider_service', 'tenant_message', 'backend_status')

        def getHumanReadableName(self, obj):
            return obj.__unicode__()

class ExampleTenantViewSet(XOSViewSet):
    base_name = "exampletenant"
    method_name = "exampletenant"
    method_kind = "viewset"
    queryset = ExampleTenant.get_tenant_objects().all()
    serializer_class = ExampleTenantSerializer

    @classmethod
    def get_urlpatterns(self, api_path="^"):
        patterns = super(ExampleTenantViewSet, self).get_urlpatterns(api_path=api_path)

        # example to demonstrate adding a custom endpoint
        patterns.append( self.detail_url("message/$", {"get": "get_message", "put": "set_message"}, "message") )

        return patterns

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def get_message(self, request, pk=None):
        example_tenant = self.get_object()
        return Response({"tenant_message": example_tenant.tenant_message})

    def set_message(self, request, pk=None):
        example_tenant = self.get_object()
        example_tenant.tenant_message = request.data["tenant_message"]
        example_tenant.save()
        return Response({"tenant_message": example_tenant.tenant_message})

