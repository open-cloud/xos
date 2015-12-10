from rest_framework import generics
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from xos.apibase import XOSRetrieveUpdateDestroyAPIView, XOSListCreateAPIView
from rest_framework import viewsets
from django.conf.urls import patterns, url

""" PlusSerializerMixin

    Implements Serializer fields that are common to all OpenCloud objects. For
    example, stuff related to backend fields.
"""

class PlusSerializerMixin():
    backendIcon = serializers.SerializerMethodField("getBackendIcon")
    backendHtml = serializers.SerializerMethodField("getBackendHtml")

    # This will cause a descendant class to pull in the methods defined
    # above. See rest_framework/serializers.py: _get_declared_fields().
    base_fields = {"backendIcon": backendIcon, "backendHtml": backendHtml}
    # Rest_framework 3.0 uses _declared_fields instead of base_fields
    _declared_fields = {"backendIcon": backendIcon, "backendHtml": backendHtml}

    def getBackendIcon(self, obj):
        return obj.getBackendIcon()

    def getBackendHtml(self, obj):
        return obj.getBackendHtml()

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
