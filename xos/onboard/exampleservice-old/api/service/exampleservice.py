from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import detail_route, list_route
from rest_framework.views import APIView
from core.models import *
from django.forms import widgets
from django.conf.urls import patterns, url
from api.xosapi_helpers import PlusModelSerializer, XOSViewSet, ReadOnlyField
from django.shortcuts import get_object_or_404
from xos.apibase import XOSListCreateAPIView, XOSRetrieveUpdateDestroyAPIView, XOSPermissionDenied
from xos.exceptions import *
import json
import subprocess
from services.exampleservice.models import ExampleService

class ExampleServiceSerializer(PlusModelSerializer):
        id = ReadOnlyField()
        humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
        service_message = serializers.CharField(required=False)

        class Meta:
            model = ExampleService
            fields = ('humanReadableName',
                      'id',
                      'service_message')

        def getHumanReadableName(self, obj):
            return obj.__unicode__()

class ExampleServiceViewSet(XOSViewSet):
    base_name = "exampleservice"
    method_name = "exampleservice"
    method_kind = "viewset"
    queryset = ExampleService.get_service_objects().all()
    serializer_class = ExampleServiceSerializer

    @classmethod
    def get_urlpatterns(self, api_path="^"):
        patterns = super(ExampleServiceViewSet, self).get_urlpatterns(api_path=api_path)

        return patterns

    def list(self, request):
        object_list = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(object_list, many=True)

        return Response(serializer.data)

