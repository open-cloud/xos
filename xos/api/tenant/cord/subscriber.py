from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.views import APIView
from core.models import *
from django.forms import widgets
from django.conf.urls import patterns, url
from services.cord.models import VOLTTenant, VBNGTenant, CordSubscriberRoot
from core.xoslib.objects.cordsubscriber import CordSubscriber
from api.xosapi_helpers import PlusSerializerMixin, XOSViewSet
from django.shortcuts import get_object_or_404
from xos.apibase import XOSListCreateAPIView, XOSRetrieveUpdateDestroyAPIView, XOSPermissionDenied
from xos.exceptions import *
import json
import subprocess

if hasattr(serializers, "ReadOnlyField"):
    # rest_framework 3.x
    ReadOnlyField = serializers.ReadOnlyField
else:
    # rest_framework 2.x
    ReadOnlyField = serializers.Field

class CordSubscriberIdSerializer(serializers.ModelSerializer, PlusSerializerMixin):
        id = ReadOnlyField()
        service_specific_id = ReadOnlyField()
        vlan_id = ReadOnlyField()      # XXX remove this
        c_tag = ReadOnlyField()
        s_tag = ReadOnlyField()
        vcpe_id = ReadOnlyField()
        instance = ReadOnlyField()
        image = ReadOnlyField()
        vbng_id = ReadOnlyField()
        firewall_enable = serializers.BooleanField()
        firewall_rules = serializers.CharField()
        url_filter_enable = serializers.BooleanField()
        url_filter_rules = serializers.CharField()
        url_filter_level = serializers.CharField(required=False)
        cdn_enable = serializers.BooleanField()
        instance_name = ReadOnlyField()
        image_name = ReadOnlyField()
        routeable_subnet = serializers.CharField(required=False)
        ssh_command = ReadOnlyField()
        bbs_account = ReadOnlyField()

        wan_container_ip = ReadOnlyField()
        uplink_speed = serializers.CharField(required=False)
        downlink_speed = serializers.CharField(required=False)
        status = serializers.CharField()
        enable_uverse = serializers.BooleanField()

        lan_ip = ReadOnlyField()
        wan_ip = ReadOnlyField()
        nat_ip = ReadOnlyField()
        private_ip = ReadOnlyField()

        wan_mac = ReadOnlyField()

        vcpe_synced = serializers.BooleanField()

        humanReadableName = serializers.SerializerMethodField("getHumanReadableName")

        class Meta:
            model = CordSubscriber
            fields = ('humanReadableName', 'id',
                      'service_specific_id', 'vlan_id', 's_tag', 'c_tag',
                      'vcpe_id', 'instance', 'instance_name', 'image', 'image_name',
                      'firewall_enable', 'firewall_rules',
                      'url_filter_enable', 'url_filter_rules', 'url_filter_level',
                      'bbs_account',
                      'ssh_command',
                      'vcpe_synced',
                      'cdn_enable', 'vbng_id', 'routeable_subnet', 'nat_ip', 'lan_ip', 'wan_ip', 'private_ip', 'wan_mac',
                      'wan_container_ip',
                      'uplink_speed', 'downlink_speed', 'status', 'enable_uverse')


        def getHumanReadableName(self, obj):
            return obj.__unicode__()

#------------------------------------------------------------------------------
# The "old" API
# This is used by the xoslib-based GUI
#------------------------------------------------------------------------------

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


#------------------------------------------------------------------------------
# The "new" API with many more REST endpoints.
# This is for integration with with the subscriber GUI
#------------------------------------------------------------------------------

class CordSubscriberViewSet(XOSViewSet):
    base_name = "subscriber"
    method_name = "subscriber"
    method_kind = "viewset"
    queryset = CordSubscriber.get_tenant_objects().select_related().all()
    serializer_class = CordSubscriberIdSerializer

    def get_vcpe(self):
        subscriber = self.get_object()
        if not subscriber.vcpe:
            raise XOSMissingField("vCPE object is not present for subscriber")
        return subscriber.vcpe

    @classmethod
    def get_urlpatterns(self, api_path="^"):
        patterns = super(CordSubscriberViewSet, self).get_urlpatterns(api_path=api_path)
        patterns.append( self.detail_url("vcpe_synced/$", {"get": "get_vcpe_synced"}, "vcpe_synced") )
        patterns.append( self.detail_url("url_filter/$", {"get": "get_url_filter"}, "url_filter") )
        patterns.append( self.detail_url("url_filter/(?P<level>[a-zA-Z0-9\-_]+)/$", {"put": "set_url_filter"}, "url_filter") )
        patterns.append( self.detail_url("services/$", {"get": "get_services"}, "services") )
        patterns.append( self.detail_url("services/(?P<service>[a-zA-Z0-9\-_]+)/$", {"get": "get_service"}, "get_service") )
        patterns.append( self.detail_url("services/(?P<service>[a-zA-Z0-9\-_]+)/true/$", {"put": "enable_service"}, "enable_service") )
        patterns.append( self.detail_url("services/(?P<service>[a-zA-Z0-9\-_]+)/false/$", {"put": "disable_service"}, "disable_service") )

        patterns.append( self.detail_url("users/$", {"get": "get_users", "post": "create_user"}, "users") )
        patterns.append( self.detail_url("users/clearusers/$", {"get": "clear_users", "put": "clear_users", "post": "clear_users"}, "clearusers") )
        patterns.append( self.detail_url("users/newuser/$", {"put": "create_user", "post": "create_user"}, "newuser") )
        patterns.append( self.detail_url("users/(?P<uid>[0-9\-]+)/$", {"delete": "delete_user"}, "user") )
        patterns.append( self.detail_url("users/(?P<uid>[0-9\-]+)/url_filter/$", {"get": "get_user_level"}, "user_level") )
        patterns.append( self.detail_url("users/(?P<uid>[0-9\-]+)/url_filter/(?P<level>[a-zA-Z0-9\-_]+)/$", {"put": "set_user_level"}, "set_user_level") )

        patterns.append( self.detail_url("bbsdump/$", {"get": "get_bbsdump"}, "bbsdump") )

        patterns.append( url(self.api_path + "subidlookup/(?P<ssid>[0-9\-]+)/$", self.as_view({"get": "ssiddetail"}), name="ssiddetail") )
        patterns.append( url(self.api_path + "subidlookup/$", self.as_view({"get": "ssidlist"}), name="ssidlist") )

        return patterns

    def list(self, request):
        object_list = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(object_list, many=True)

        return Response({"subscribers": serializer.data})

    def get_vcpe_synced(self, request, pk=None):
        subscriber = self.get_object()
        return Response({"vcpe_synced": subscriber.vcpe_synced})

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
        return Response(subscriber.users)

    def get_user_level(self, request, pk=None, uid=None):
        subscriber = self.get_object()
        user = subscriber.find_user(uid)
        if user and user.get("level", None):
            level = user["level"]
        else:
            level = self.get_object().url_filter_level

        return Response( {"id": uid, "level": level} )

    def set_user_level(self, request, pk=None, uid=None, level=None):
        subscriber = self.get_object()
        subscriber.update_user(uid, level=level)
        subscriber.save()
        return self.get_user_level(request, pk, uid)

    def create_user(self, request, pk=None):
        data = request.DATA
        name = data.get("name",None)
        mac = data.get("mac",None)
        if (not name):
             raise XOSMissingField("name must be specified when creating user")
        if (not mac):
             raise XOSMissingField("mac must be specified when creating user")

        subscriber = self.get_object()
        newuser = subscriber.create_user(name=name, mac=mac)
        subscriber.save()

        return Response(newuser)

    def delete_user(self, request, pk=None, uid=None):
        subscriber = self.get_object()
        subscriber.delete_user(uid)
        subscriber.save()

        return Response( {"id": uid, "deleted": True} )

    def clear_users(self, request, pk=None):
        subscriber = self.get_object()
        subscriber.users = []
        subscriber.save()

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

    def get_bbsdump(self, request, pk=None):
        subscriber = self.get_object()
        if not subsciber.volt or not subscriber.volt.vcpe:
            raise XOSMissingField("subscriber has no vCPE")
        if not subscriber.volt.vcpe.bbs_account:
            raise XOSMissingField("subscriber has no bbs_account")

        result=subprocess.check_output(["python", "/opt/xos/observers/vcpe/broadbandshield.py", "dump", subscriber.volt.vcpe.bbs_account, "123"])
        if request.GET.get("theformat",None)=="text":
            from django.http import HttpResponse
            return HttpResponse(result, content_type="text/plain")
        else:
            return Response( {"bbs_dump": result } )

    def setup_demo_subscriber(self, subscriber):
        # nuke the users and start over
        subscriber.users = []
        subscriber.create_user(name="Mom's PC",      mac="010203040506", level="PG_13")
        subscriber.create_user(name="Dad's PC",      mac="90E2Ba82F975", level="PG_13")
        subscriber.create_user(name="Jack's Laptop", mac="685B359D91D5", level="PG_13")
        subscriber.create_user(name="Jill's Laptop", mac="34363BC9B6A6", level="PG_13")
        subscriber.save()

    def initdemo(self, request):
        object_list = CordSubscriber.get_tenant_objects().all()

        # reset the parental controls in any existing demo vCPEs
        for o in object_list:
            if str(o.service_specific_id) in ["0", "1"]:
                self.setup_demo_subscriber(o)

        demo_subscribers = [o for o in object_list if o.is_demo_user]

        if demo_subscribers:
            return Response({"id": demo_subscribers[0].id})

        subscriber = CordSubscriberRoot(service_specific_id=1234,
                                        name="demo-subscriber",)
        subscriber.is_demo_user = True
        subscriber.save()

        self.setup_demo_subscriber(subscriber)

        return Response({"id": subscriber.id})

    def ssidlist(self, request):
        object_list = CordSubscriber.get_tenant_objects().all()

        ssidmap = [ {"service_specific_id": x.service_specific_id, "subscriber_id": x.id} for x in object_list ]

        return Response({"ssidmap": ssidmap})

    def ssiddetail(self, pk=None, ssid=None):
        object_list = CordSubscriber.get_tenant_objects().all()

        ssidmap = [ {"service_specific_id": x.service_specific_id, "subscriber_id": x.id} for x in object_list if str(x.service_specific_id)==str(ssid) ]

        if len(ssidmap)==0:
            raise XOSNotFound("didn't find ssid %s" % str(ssid))

        return Response( ssidmap[0] )

