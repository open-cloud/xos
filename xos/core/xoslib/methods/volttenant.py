from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from core.models import *
from django.forms import widgets
from cord.models import VOLTTenant, VOLTService
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
        vlan_id = serializers.CharField()
        provider_service = serializers.PrimaryKeyRelatedField(queryset=VOLTService.get_service_objects().all(), default=get_default_volt_service)

        humanReadableName = serializers.SerializerMethodField("getHumanReadableName")

        class Meta:
            model = VOLTTenant
            fields = ('humanReadableName', 'id', 'provider_service', 'service_specific_id', 'vlan_id' )

        def getHumanReadableName(self, obj):
            return obj.__unicode__()

class VOLTTenantList(XOSListCreateAPIView):
    queryset = VOLTTenant.get_tenant_objects().select_related().all()
    serializer_class = VOLTTenantIdSerializer

    method_kind = "list"
    method_name = "volttenant"

class VOLTTenantDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = VOLTTenant.get_tenant_objects().select_related().all()
    serializer_class = VOLTTenantIdSerializer

    method_kind = "detail"
    method_name = "volttenant"


