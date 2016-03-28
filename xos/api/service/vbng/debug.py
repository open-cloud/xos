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

class CordDebugIdSerializer(serializers.ModelSerializer, PlusSerializerMixin):
    # Swagger is failing because CordDebugViewSet has neither a model nor
    # a serializer_class. Stuck this in here as a placeholder for now.
    id = ReadOnlyField()
    class Meta:
        model = CordSubscriber

class CordDebugViewSet(XOSViewSet):
    base_name = "debug"
    method_name = "debug"
    method_kind = "viewset"
    serializer_class = CordDebugIdSerializer

    @classmethod
    def get_urlpatterns(self, api_path="^"):
        patterns = []
        patterns.append( url(api_path + "debug/vbng_dump/$", self.as_view({"get": "get_vbng_dump"}), name="vbng_dump"))
        return patterns

    # contact vBNG service and dump current list of mappings
    def get_vbng_dump(self, request, pk=None):
        result=subprocess.check_output(["curl", "http://10.0.3.136:8181/onos/virtualbng/privateip/map"])
        if request.GET.get("theformat",None)=="text":
            from django.http import HttpResponse
            result = json.loads(result)["map"]

            lines = []
            for row in result:
                for k in row.keys():
                     lines.append( "%s %s" % (k, row[k]) )

            return HttpResponse("\n".join(lines), content_type="text/plain")
        else:
            return Response( {"vbng_dump": json.loads(result)["map"] } )
