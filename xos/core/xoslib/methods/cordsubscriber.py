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
from xos.exceptions import *
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
        bbs_account = ReadOnlyField()

        lan_ip = ReadOnlyField()
        wan_ip = ReadOnlyField()
        nat_ip = ReadOnlyField()
        private_ip = ReadOnlyField()

        humanReadableName = serializers.SerializerMethodField("getHumanReadableName")

        class Meta:
            model = CordSubscriber
            fields = ('humanReadableName', 'id',
                      'service_specific_id', 'vlan_id',
                      'vcpe_id', 'sliver', 'sliver_name', 'image', 'image_name',
                      'firewall_enable', 'firewall_rules',
                      'url_filter_enable', 'url_filter_rules', 'url_filter_level',
                      'bbs_account',
                      'cdn_enable', 'vbng_id', 'routeable_subnet', 'nat_ip', 'lan_ip', 'wan_ip', 'private_ip')


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
    def list_url(self, pattern, viewdict, name):
        return url(r'^' + self.method_name + r'/' + pattern,
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

    def get_vcpe(self):
        subscriber = self.get_object()
        if not subscriber.vcpe:
            raise XOSMissingField("vCPE object is not present for subscriber")
        return subscriber.vcpe

    @classmethod
    def get_urlpatterns(self):
        patterns = super(CordSubscriberViewSet, self).get_urlpatterns()
        patterns.append( self.detail_url("url_filter/$", {"get": "get_url_filter"}, "url_filter") )
        patterns.append( self.detail_url("url_filter/(?P<level>[a-zA-Z0-9\-]+)/$", {"put": "set_url_filter"}, "url_filter") )
        patterns.append( self.detail_url("services/$", {"get": "get_services"}, "services") )
        patterns.append( self.detail_url("services/(?P<service>[a-zA-Z0-9\-_]+)/$", {"get": "get_service"}, "get_service") )
        patterns.append( self.detail_url("services/(?P<service>[a-zA-Z0-9\-_]+)/true/$", {"put": "enable_service"}, "enable_service") )
        patterns.append( self.detail_url("services/(?P<service>[a-zA-Z0-9\-_]+)/false/$", {"put": "disable_service"}, "disable_service") )

        patterns.append( self.detail_url("users/$", {"get": "get_users", "post": "create_user"}, "users") )
        patterns.append( self.detail_url("users/clearusers/$", {"get": "clear_users", "put": "clear_users", "post": "clear_users"}, "clearusers") )
        patterns.append( self.detail_url("users/newuser/$", {"put": "create_user", "post": "create_user"}, "newuser") )
        patterns.append( self.detail_url("users/(?P<uid>[0-9\-]+)/$", {"delete": "delete_user"}, "user") )
        patterns.append( self.detail_url("users/(?P<uid>[0-9\-]+)/url_filter/$", {"get": "get_user_level"}, "user_level") )
        patterns.append( self.detail_url("users/(?P<uid>[0-9\-]+)/url_filter/(?P<level>[a-zA-Z0-9\-]+)/$", {"put": "set_user_level"}, "set_user_level") )

        patterns.append( url("^rs/initdemo/$", self.as_view({"put": "initdemo", "get": "initdemo"}), name="initdemo") )

        return patterns

    def list(self, request):
        object_list = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(object_list, many=True)

        return Response({"subscribers": serializer.data})

    def get_url_filter(self, request, pk=None):
        subscriber = self.get_object()
        return Response({"level": subscriber.url_filter_level})

    def set_url_filter(self, request, pk=None, level=None):
        subscriber = self.get_object()
        subscriber.url_filter_level = level
        subscriber.save()
        return Response({"level": subscriber.url_filter_level})

    def get_users(self, request, pk=None):
        subscriber = self.get_object()
        return Response({"users": subscriber.users})

    def get_user_level(self, request, pk=None, uid=None):
        vcpe = self.get_vcpe()
        user = vcpe.find_user(uid)
        if user and user.get("level", None):
            level = user["level"]
        else:
            level = self.get_object().url_filter_level

        return Response( {"id": uid, "level": level} )

    def set_user_level(self, request, pk=None, uid=None, level=None):
        vcpe = self.get_vcpe()
        vcpe.update_user(uid, level=level)
        vcpe.save()
        return self.get_user_level(request, pk, uid)

    def create_user(self, request, pk=None):
        vcpe = self.get_vcpe()

        data = request.DATA
        name = data.get("name",None)
        mac = data.get("mac",None)
        if (not name):
             raise XOSMissingField("name must be specified when creating user")
        if (not mac):
             raise XOSMissingField("mac must be specified when creating user")

        newuser = vcpe.create_user(name=name, mac=mac)
        vcpe.save()

        return Response(newuser)

    def delete_user(self, request, pk=None, uid=None):
        vcpe = self.get_vcpe()

        vcpe.delete_user(uid)
        vcpe.save()

        return Response( {"id": uid, "deleted": True} )

    def clear_users(self, request, pk=None):
        vcpe = self.get_vcpe()
        vcpe.users = []
        vcpe.save()

        return Response( "Okay" )

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

    def initdemo(self, request):
        object_list = VOLTTenant.get_tenant_objects().all()

        demo_subscribers = [o for o in object_list if o.is_demo_user]

        if demo_subscribers:
            return Response({"id": demo_subscribers[0].id})

        voltTenant = VOLTTenant(service_specific_id=1234,
                                vlan_id=1234,
                                is_demo_user=True)
        voltTenant.caller = User.objects.get(email="padmin@vicci.org")
        voltTenant.save()

        voltTenant.vcpe.create_user(name="Mom's PC",      mac="01020303040506", level="R")
        voltTenant.vcpe.create_user(name="Dad's PC",      mac="01020304040507", level="R")
        voltTenant.vcpe.create_user(name="Jack's iPhone", mac="01020304050508", level="PG")
        voltTenant.vcpe.create_user(name="Jill's iPad",   mac="01020304050609", level="G")
        voltTenant.vcpe.save()

        return Response({"id": voltTenant.id})

