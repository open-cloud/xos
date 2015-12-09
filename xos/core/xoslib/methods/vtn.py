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
from plus import PlusSerializerMixin, XOSViewSet
from django.shortcuts import get_object_or_404
from xos.apibase import XOSListCreateAPIView, XOSRetrieveUpdateDestroyAPIView, XOSPermissionDenied
from xos.exceptions import *
import json
import subprocess

class VTNViewSet(XOSViewSet):
    base_name = "vtn"
    method_name = "rs/vtn"
    method_kind = "viewset"

    # these are just because ViewSet needs some queryset and model, even if we don't use the
    # default endpoints
    queryset = Service.objects.none() # CordSubscriber.get_tenant_objects().select_related().all()
    model = Service

    @classmethod
    def get_urlpatterns(self):
        patterns = []
        patterns.append( self.list_url("services/$", {"get": "get_services"}, "services") )
        patterns.append( self.list_url("services/(?P<service>[a-zA-Z0-9\-_]+)/$", {"get": "get_service"}, "get_service") )

        return patterns

    def get_services(self, request, pk=None):
        result = {}
        for service in Service.objects.all():
           result[service.id] = service.get_vtn_dependencies()
        return Response(result)

    def get_service(self, request, pk=None, service=None):
        result=Service.objects.get(pk = service).get_vtn_dependencies()
        return Response(result)

    def list(self, request):
        raise Exception("Not Implemented")

