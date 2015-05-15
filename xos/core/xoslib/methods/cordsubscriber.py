from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from core.models import *
from django.forms import widgets
from django.conf.urls import patterns, url
from cord.models import VOLTTenant
from core.xoslib.objects.cordsubscriber import CordSubscriber
from plus import PlusSerializerMixin
from django.shortcuts import get_object_or_404
from xos.apibase import XOSListCreateAPIView, XOSRetrieveUpdateDestroyAPIView, XOSPermissionDenied
import json

if hasattr(serializers, "ReadOnlyField"):
    # rest_framework 3.x
    ReadOnlyField = serializers.ReadOnlyField
else:
    # rest_framework 2.x
    ReadOnlyField = serializers.Field

class CordSubscriberIdSerializer(serializers.ModelSerializer, PlusSerializerMixin):
        id = ReadOnlyField()
        service_specific_id = ReadOnlyField()
        vlan_id = ReadOnlyField()
        vcpe_id = ReadOnlyField()
        sliver = ReadOnlyField()
        image = ReadOnlyField()
        vbng_id = ReadOnlyField()
        firewall_enable = serializers.BooleanField()
        firewall_rules = serializers.CharField()
        url_filter_enable = serializers.BooleanField()
        url_filter_rules = serializers.CharField()
        url_filter_level = serializers.CharField(required=False)
        cdn_enable = serializers.BooleanField()
        sliver_name = ReadOnlyField()
        image_name = ReadOnlyField()
        routeable_subnet = serializers.CharField(required=False)

        humanReadableName = serializers.SerializerMethodField("getHumanReadableName")

        class Meta:
            model = CordSubscriber
            fields = ('humanReadableName', 'id',
                      'service_specific_id', 'vlan_id',
                      'vcpe_id', 'sliver', 'sliver_name', 'image', 'image_name', 'firewall_enable', 'firewall_rules', 'url_filter_enable', 'url_filter_rules', 'url_filter_level', 'cdn_enable', 'vbng_id', 'routeable_subnet',)


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

# this may be moved into plus.py...

class XOSViewSet(viewsets.ModelViewSet):
    @classmethod
    def detail_url(self, pattern, viewdict, name):
        return url(r'^' + self.method_name + r'/(?P<pk>[a-zA-Z0-9\-]+)/' + pattern,
                   self.as_view(viewdict),
                   name=self.base_name+"_"+name)

    @classmethod
    def get_urlpatterns(self):
        patterns = []

        patterns.append(url(r'^' + self.method_name + '/$', self.as_view({'get': 'list'}), name=self.base_name+'_list'))
        patterns.append(url(r'^' + self.method_name + '/(?P<pk>[a-zA-Z0-9\-]+)/$', self.as_view({'get': 'retrieve', 'put': 'update', 'post': 'update', 'delete': 'destroy', 'patch': 'partial_update'}), name=self.base_name+'_detail'))

        return patterns

# the "new" API with many more REST endpoints.

class CordSubscriberViewSet(XOSViewSet):
    base_name = "subscriber"
    method_name = "rs/subscriber"
    method_kind = "viewset"
    queryset = CordSubscriber.get_tenant_objects().select_related().all()
    serializer_class = CordSubscriberIdSerializer

    @classmethod
    def get_urlpatterns(self):
        patterns = super(CordSubscriberViewSet, self).get_urlpatterns()
        patterns.append( self.detail_url("url_filtering/$", {"get": "get_url_filtering"}, "url_filtering") )
        patterns.append( self.detail_url("url_filtering/(?P<level>[a-zA-Z0-9\-]+)/$", {"get": "set_url_filtering"}, "url_filtering") )
        patterns.append( self.detail_url("users/$", {"get": "get_users"}, "users") )
        patterns.append( self.detail_url("services/$", {"get": "get_services"}, "services") )
        patterns.append( self.detail_url("services/(?P<service>[a-zA-Z0-9\-]+)/$", {"get": "get_service"}, "get_service") )
        patterns.append( self.detail_url("services/(?P<service>[a-zA-Z0-9\-]+)/true/$", {"get": "enable_service"}, "enable_service") )
        patterns.append( self.detail_url("services/(?P<service>[a-zA-Z0-9\-]+)/false/$", {"get": "disable_service"}, "disable_service") )

        return patterns

    def list(self, request):
        object_list = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(object_list, many=True)

        return Response({"subscribers": serializer.data})

    def get_url_filtering(self, request, pk=None):
        subscriber = self.get_object()
        return Response({"level": subscriber.url_filter_level})

    def set_url_filtering(self, request, pk=None, level=None):
        subscriber = self.get_object()
        subscriber.url_filter_level = level
        subscriber.save()
        return Response({"level": subscriber.url_filter_level})

    def get_users(self, request, pk=None):
        subscriber = self.get_object()
        return Response({"users": subscriber.users})

    def get_services(self, request, pk=None):
        subscriber = self.get_object()
        return Response(subscriber.services)

    def get_service(self, request, pk=None, service=None):
        service_attr = service+"_enable"
        subscriber = self.get_object()
        return Response({service: getattr(subscriber, service_attr)})

    def enable_service(self, request, pk=None, service=None):
        service_attr = service+"_enable"
        subscriber = self.get_object()
        setattr(subscriber, service_attr, True)
        subscriber.save()
        return Response({service: getattr(subscriber, service_attr)})

    def disable_service(self, request, pk=None, service=None):
        service_attr = service+"_enable"
        subscriber = self.get_object()
        setattr(subscriber, service_attr, False)
        subscriber.save()
        return Response({service: getattr(subscriber, service_attr)})




