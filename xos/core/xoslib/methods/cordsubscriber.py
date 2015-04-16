from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from core.models import *
from django.forms import widgets
from cord.models import VOLTTenant
from core.xoslib.objects.cordsubscriber import CordSubscriber
from plus import PlusSerializerMixin
from xos.apibase import XOSListCreateAPIView, XOSRetrieveUpdateDestroyAPIView, XOSPermissionDenied

if hasattr(serializers, "ReadOnlyField"):
    # rest_framework 3.x
    IdField = serializers.ReadOnlyField
else:
    # rest_framework 2.x
    IdField = serializers.Field

class CordSubscriberIdSerializer(serializers.ModelSerializer, PlusSerializerMixin):
        id = IdField()
        vcpe_id = IdField()
        sliver_id = IdField()
        firewall_enable = serializers.BooleanField()

        humanReadableName = serializers.SerializerMethodField("getHumanReadableName")

        class Meta:
            model = CordSubscriber
            fields = ('humanReadableName', 'id',
                      'service_specific_id',
                      'vcpe_id', 'sliver_id', 'firewall_enable')


        def getHumanReadableName(self, obj):
            return str(obj)

class CordSubscriberList(XOSListCreateAPIView):
    queryset = CordSubscriber.get_tenant_objects().select_related().all()
    serializer_class = CordSubscriberIdSerializer

    method_kind = "list"
    method_name = "cordsubscriber"

class CordSubscriberDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = CordSubscriber.get_tenant_objects().select_related().all()
    serializer_class = CordSubscriberIdSerializer

    method_kind = "detail"
    method_name = "cordsubscriber"


