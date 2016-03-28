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
from api.xosapi_helpers import PlusSerializerMixin, XOSViewSet, ReadOnlyField
from django.shortcuts import get_object_or_404
from xos.apibase import XOSListCreateAPIView, XOSRetrieveUpdateDestroyAPIView, XOSPermissionDenied
from xos.exceptions import *
import json
import subprocess
from django.views.decorators.csrf import ensure_csrf_cookie

class CordSubscriberNew(CordSubscriberRoot):
    class Meta:
        proxy = True
        app_label = "cord"

    def __init__(self, *args, **kwargs):
        super(CordSubscriberNew, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return u"cordSubscriber-%s" % str(self.id)

    @property
    def features(self):
        return {"cdn": self.cdn_enable,
                "uplink_speed": self.uplink_speed,
                "downlink_speed": self.downlink_speed,
                "uverse": self.enable_uverse,
                "status": self.status}

    @features.setter
    def features(self, value):
        self.cdn_enable = value.get("cdn", self.get_default_attribute("cdn_enable"))
        self.uplink_speed = value.get("uplink_speed", self.get_default_attribute("uplink_speed"))
        self.downlink_speed = value.get("downlink_speed", self.get_default_attribute("downlink_speed"))
        self.enable_uverse = value.get("uverse", self.get_default_attribute("enable_uverse"))
        self.status = value.get("status", self.get_default_attribute("status"))

    def save(self, *args, **kwargs):
        super(CordSubscriberNew, self).save(*args, **kwargs)

#class FeatureSerializer(serializers.Serializer):
#    cdn = serializers.BooleanField()
#    uplink_speed = serializers.IntegerField()
#    downlink_speed = serializers.IntegerField()
#    uverse = serializers.BooleanField()
#    status = serializers.CharField()

class CordSubscriberSerializer(serializers.ModelSerializer, PlusSerializerMixin):
        id = ReadOnlyField()
        service_specific_id = ReadOnlyField()
        humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
        features = serializers.DictField()

        class Meta:
            model = CordSubscriberNew
            fields = ('humanReadableName',
                      'id',
                      'service_specific_id',
                      'features')

        def getHumanReadableName(self, obj):
            return obj.__unicode__()

# @ensure_csrf_cookie
class CordSubscriberViewSet(XOSViewSet):
    base_name = "subscriber"
    method_name = "subscriber"
    method_kind = "viewset"
    queryset = CordSubscriberNew.get_tenant_objects().select_related().all()
    serializer_class = CordSubscriberSerializer

    @classmethod
    def get_urlpatterns(self, api_path="^"):
        patterns = super(CordSubscriberViewSet, self).get_urlpatterns(api_path=api_path)
        patterns.append( self.detail_url("features/$", {"get": "get_features", "put": "set_features"}, "features") )
        patterns.append( self.detail_url("features/(?P<feature>[a-zA-Z0-9\-_]+)/$", {"get": "get_feature", "put": "set_feature"}, "get_feature") )

        patterns.append( url(self.api_path + "subidlookup/(?P<ssid>[0-9\-]+)/$", self.as_view({"get": "ssiddetail"}), name="ssiddetail") )
        patterns.append( url(self.api_path + "subidlookup/$", self.as_view({"get": "ssidlist"}), name="ssidlist") )

        return patterns

    def list(self, request):
        object_list = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(object_list, many=True)

        return Response({"subscribers": serializer.data})

    def get_features(self, request, pk=None):
        subscriber = self.get_object()
        return Response(subscriber.features)

    def get_feature(self, request, pk=None, feature=None):
        subscriber = self.get_object()
        return Response(subscriber.features[feature])

    def set_feature(self, request, pk=None, feature=None):
        subscriber = self.get_object()
        subscriber.features[feature] = request.data
        print "XXX", request.DATA
        return Response(subscriber.features[feature])

    def set_features(self, request, pk=None):
        subscriber = self.get_object()
        for k in subscriber.features:
            subscriber.features[k] = request.data.get(k, subscriber.features[k])
        return Response(subscriber.features[feature])

    def ssidlist(self, request):
        object_list = CordSubscriberNew.get_tenant_objects().all()

        ssidmap = [ {"service_specific_id": x.service_specific_id, "subscriber_id": x.id} for x in object_list ]

        return Response({"ssidmap": ssidmap})

    def ssiddetail(self, pk=None, ssid=None):
        object_list = CordSubscriberNew.get_tenant_objects().all()

        ssidmap = [ {"service_specific_id": x.service_specific_id, "subscriber_id": x.id} for x in object_list if str(x.service_specific_id)==str(ssid) ]

        if len(ssidmap)==0:
            raise XOSNotFound("didn't find ssid %s" % str(ssid))

        return Response( ssidmap[0] )

