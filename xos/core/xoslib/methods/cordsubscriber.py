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
    ReadOnlyField = serializers.ReadOnlyField
else:
    # rest_framework 2.x
    ReadOnlyField = serializers.Field

class CordSubscriberIdSerializer(serializers.ModelSerializer, PlusSerializerMixin):
        id = ReadOnlyField()
        vcpe_id = ReadOnlyField()
        sliver = ReadOnlyField()
        image = ReadOnlyField()
        firewall_enable = serializers.BooleanField()
        firewall_rules = serializers.CharField()
        url_filter_enable = serializers.BooleanField()
        url_filter_rules = serializers.CharField()
        cdn_enable = serializers.BooleanField()
        sliver_name = ReadOnlyField()
        image_name = ReadOnlyField()

        humanReadableName = serializers.SerializerMethodField("getHumanReadableName")

        class Meta:
            model = CordSubscriber
            fields = ('humanReadableName', 'id',
                      'service_specific_id',
                      'vcpe_id', 'sliver', 'sliver_name', 'image', 'image_name', 'firewall_enable', 'firewall_rules', 'url_filter_enable', 'url_filter_rules', 'cdn_enable')


        def getHumanReadableName(self, obj):
            return obj.__unicode__()

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


