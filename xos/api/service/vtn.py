from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.views import APIView
from core.models import *
from services.vtn.models import VTNService
from django.forms import widgets
from django.conf.urls import patterns, url
from api.xosapi_helpers import PlusModelSerializer, XOSViewSet, ReadOnlyField
from django.shortcuts import get_object_or_404
from xos.apibase import XOSListCreateAPIView, XOSRetrieveUpdateDestroyAPIView, XOSPermissionDenied
from xos.exceptions import *
import json
import subprocess

class VTNServiceSerializer(PlusModelSerializer):
    id = ReadOnlyField()

    privateGatewayMac = serializers.CharField(required=False)
    localManagementIp = serializers.CharField(required=False)
    ovsdbPort = serializers.IntegerField(required=False)
    sshPort = serializers.IntegerField(required=False)
    sshUser = serializers.CharField(required=False)
    sshKeyFile = serializers.CharField(required=False)
    mgmtSubnetBits = serializers.IntegerField(required=False)
    xosEndpoint = serializers.CharField(required=False)
    xosUser = serializers.CharField(required=False)
    xosPassword = serializers.CharField(required=False)


    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    class Meta:
        model = VTNService
        fields = ('humanReadableName', 'id', 'privateGatewayMac', 'localManagementIp', 'ovsdbPort', 'sshPort', 'sshUser', 'sshKeyFile',
                  'mgmtSubnetBits', 'xosEndpoint', 'xosUser', 'xosPassword')

    def getHumanReadableName(self, obj):
        return obj.__unicode__()

class VTNViewSet(XOSViewSet):
    base_name = "vtn"
    method_name = "vtn"
    method_kind = "viewset"

    # these are just because ViewSet needs some queryset and model, even if we don't use the
    # default endpoints
    queryset = VTNService.get_service_objects().all()
    model = VTNService
    serializer_class = VTNServiceSerializer

    @classmethod
    def get_urlpatterns(self, api_path="^"):
        patterns = []

        patterns.append( self.detail_url("services/$", {"get": "get_services"}, "services") )
        patterns.append( self.detail_url("services_names/$", {"get": "get_services_names"}, "services") )
        patterns.append( self.detail_url("services/(?P<service>[a-zA-Z0-9\-_]+)/$", {"get": "get_service"}, "get_service") )

        # Not as RESTful as it could be, but maintain these endpoints for compability
        patterns.append( self.list_url("services/$", {"get": "get_services"}, "rootvtn_services") )
        patterns.append( self.list_url("services_names/$", {"get": "get_services_names"}, "rootvtn_services") )
        patterns.append( self.list_url("services/(?P<service>[a-zA-Z0-9\-_]+)/$", {"get": "get_service"}, "rootvtn_get_service") )

        patterns = patterns + super(VTNViewSet,self).get_urlpatterns(api_path)

        return patterns

    def get_services_names(self, request, pk=None):
        result = {}
        for service in Service.objects.all():
           for id in service.get_vtn_src_names():
               dependencies = service.get_vtn_dependencies_names()
               if dependencies:
                   result[id] = dependencies
        return Response(result)

    def get_services(self, request, pk=None):
        result = {}
        for service in Service.objects.all():
           for id in service.get_vtn_src_ids():
               dependencies = service.get_vtn_dependencies_ids()
               if dependencies:
                   result[id] = dependencies
        return Response(result)

    def get_service(self, request, pk=None, service=None):
        for xos_service in Service.objects.all():
            if service in xos_service.get_vtn_src_ids():
                return Response(xos_service.get_vtn_dependencies_ids())
        return Response([])


