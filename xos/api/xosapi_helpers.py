from rest_framework import generics
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from xos.apibase import XOSRetrieveUpdateDestroyAPIView, XOSListCreateAPIView
from rest_framework import viewsets
from django.conf.urls import patterns, url
from xos.exceptions import *
from rest_framework.reverse import reverse
from django.core.urlresolvers import get_script_prefix, resolve, Resolver404

# rest_framework 3.x
ReadOnlyField = serializers.ReadOnlyField

ICON_URLS = {"success": "/static/admin/img/icon_success.gif",
            "clock": "/static/admin/img/icon_clock.gif",
            "error": "/static/admin/img/icon_error.gif"}

class PlusObjectMixin:
    def getBackendIcon(self):
        (icon, tooltip) = self.get_backend_icon()
        icon_url = ICON_URLS.get(icon, "unknown")
        return icon_url

    def getBackendHtml(self):
        (icon, tooltip) = self.get_backend_icon()
        icon_url = ICON_URLS.get(icon, "unknown")

        if tooltip:
            return '<span title="%s"><img src="%s"></span>' % (tooltip, icon_url)
        else:
            return '<img src="%s">' % icon_url

""" PlusSerializerMixin

    Implements Serializer fields that are common to all OpenCloud objects. For
    example, stuff related to backend fields.
"""

class PlusModelSerializer(serializers.ModelSerializer):
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

    def create(self, validated_data):
        property_fields = getattr(self, "property_fields", [])
        create_fields = {}
        for k in validated_data:
            if not k in property_fields:
                create_fields[k] = validated_data[k]
        instance = self.Meta.model(**create_fields)

        if instance and hasattr(instance,"can_update") and self.context.get('request',None):
            user = self.context['request'].user
            if user.__class__.__name__=="AnonymousUser":
                raise XOSPermissionDenied()
            if not instance.can_update(user):
                raise XOSPermissionDenied()

        for k in validated_data:
            if k in property_fields:
                setattr(instance, k, validated_data[k])

        instance.caller = self.context['request'].user
        instance.save()
        return instance

    def update(self, instance, validated_data):
        nested_fields = getattr(self, "nested_fields", [])
        for k in validated_data.keys():
            v = validated_data[k]
            if k in nested_fields:
                d = getattr(instance,k)
                d.update(v)
                setattr(instance,k,d)
            else:
                setattr(instance, k, v)
        instance.caller = self.context['request'].user
        instance.save()
        return instance

class XOSViewSet(viewsets.ModelViewSet):
    api_path=""
    read_only=False

    @classmethod
    def get_api_method_path(self):
        if self.method_name:
            return self.api_path + self.method_name + "/"
        else:
            return self.api_path

    @classmethod
    def detail_url(self, pattern, viewdict, name):
        return url(self.get_api_method_path() + r'(?P<pk>[a-zA-Z0-9\-_]+)/' + pattern,
                   self.as_view(viewdict),
                   name=self.base_name+"_"+name)

    @classmethod
    def list_url(self, pattern, viewdict, name):
        return url(self.get_api_method_path() + pattern,
                   self.as_view(viewdict),
                   name=self.base_name+"_"+name)

    @classmethod
    def get_urlpatterns(self, api_path="^"):
        self.api_path = api_path

        patterns = []

        if self.read_only:
            patterns.append(url(self.get_api_method_path() + '$', self.as_view({'get': 'list'}), name=self.base_name+'_list'))
            patterns.append(url(self.get_api_method_path() + '(?P<pk>[a-zA-Z0-9\-_]+)/$', self.as_view({'get': 'retrieve'}), name=self.base_name+'_detail'))
        else:
            patterns.append(url(self.get_api_method_path() + '$', self.as_view({'get': 'list', 'post': 'create'}), name=self.base_name+'_list'))
            patterns.append(url(self.get_api_method_path() + '(?P<pk>[a-zA-Z0-9\-_]+)/$', self.as_view({'get': 'retrieve', 'put': 'update', 'post': 'update', 'delete': 'destroy', 'patch': 'partial_update'}), name=self.base_name+'_detail'))

        return patterns

    def get_serializer_class(self):
        if hasattr(self, "custom_serializers") and hasattr(self, "action") and (self.action in self.custom_serializers):
            return self.custom_serializers[self.action]
        else:
            return super(XOSViewSet, self).get_serializer_class()

    def get_object(self):
        obj = super(XOSViewSet, self).get_object()

        if self.action=="update" or self.action=="destroy" or self.action.startswith("set_"):
            if obj and hasattr(obj,"can_update"):
                user = self.request.user
                if user.__class__.__name__=="AnonymousUser":
                    raise XOSPermissionDenied()
                if not obj.can_update(user):
                    raise XOSPermissionDenied()

        return obj

class XOSIndexViewSet(viewsets.ViewSet):
    view_urls=[]
    subdirs=[]
    api_path = None

    def __init__(self, view_urls, subdirs, api_path):
        self.view_urls = view_urls
        self.subdirs = subdirs
        self.api_path = api_path
        super(XOSIndexViewSet, self).__init__()

    def list(self, request):
        endpoints = {}
        for view_url in self.view_urls:
            method_name = view_url[1].split("/")[-1]
            method_url = "http://" + request.get_host() + get_script_prefix() + self.api_path + "/" + method_name
            endpoints[method_name] = method_url

        for subdir in self.subdirs:
            method_name = subdir
            method_url = get_script_prefix() + self.api_path + "/" + subdir + "/"
            # Check to make sure that an endpoint exists at this method_url. This
            # prunes out subdirs that don't have any methods (like examples/)
            try:
                resolve(method_url)
            except Resolver404:
                continue
            method_url = "http://" + request.get_host() + method_url
            endpoints[method_name] = method_url

        return Response(endpoints)

