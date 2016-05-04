from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework import status
from rest_framework.generics import GenericAPIView
from services.hpc.models import *
from django.forms import widgets
from rest_framework import filters
from django.conf.urls import patterns, url
from rest_framework.exceptions import PermissionDenied as RestFrameworkPermissionDenied
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from apibase import XOSRetrieveUpdateDestroyAPIView, XOSListCreateAPIView, XOSNotAuthenticated

if hasattr(serializers, "ReadOnlyField"):
    # rest_framework 3.x
    IdField = serializers.ReadOnlyField
else:
    # rest_framework 2.x
    IdField = serializers.Field

"""
    Schema of the generator object:
        all: Set of all Model objects
        all_if(regex): Set of Model objects that match regex

    Model object:
        plural: English plural of object name
        camel: CamelCase version of object name
        refs: list of references to other Model objects
        props: list of properties minus refs

    TODO: Deal with subnets
"""

def get_hpc_REST_patterns():
    return patterns('',
        url(r'^hpcapi/$', hpc_api_root_legacy),
    # legacy - deprecated
    
        url(r'hpcapi/hpchealthchecks/$', HpcHealthCheckList.as_view(), name='hpchealthcheck-list-legacy'),
        url(r'hpcapi/hpchealthchecks/(?P<pk>[a-zA-Z0-9\-]+)/$', HpcHealthCheckDetail.as_view(), name ='hpchealthcheck-detail-legacy'),
    
        url(r'hpcapi/hpcservices/$', HpcServiceList.as_view(), name='hpcservice-list-legacy'),
        url(r'hpcapi/hpcservices/(?P<pk>[a-zA-Z0-9\-]+)/$', HpcServiceDetail.as_view(), name ='hpcservice-detail-legacy'),
    
        url(r'hpcapi/originservers/$', OriginServerList.as_view(), name='originserver-list-legacy'),
        url(r'hpcapi/originservers/(?P<pk>[a-zA-Z0-9\-]+)/$', OriginServerDetail.as_view(), name ='originserver-detail-legacy'),
    
        url(r'hpcapi/cdnprefixs/$', CDNPrefixList.as_view(), name='cdnprefix-list-legacy'),
        url(r'hpcapi/cdnprefixs/(?P<pk>[a-zA-Z0-9\-]+)/$', CDNPrefixDetail.as_view(), name ='cdnprefix-detail-legacy'),
    
        url(r'hpcapi/serviceproviders/$', ServiceProviderList.as_view(), name='serviceprovider-list-legacy'),
        url(r'hpcapi/serviceproviders/(?P<pk>[a-zA-Z0-9\-]+)/$', ServiceProviderDetail.as_view(), name ='serviceprovider-detail-legacy'),
    
        url(r'hpcapi/contentproviders/$', ContentProviderList.as_view(), name='contentprovider-list-legacy'),
        url(r'hpcapi/contentproviders/(?P<pk>[a-zA-Z0-9\-]+)/$', ContentProviderDetail.as_view(), name ='contentprovider-detail-legacy'),
    
        url(r'hpcapi/accessmaps/$', AccessMapList.as_view(), name='accessmap-list-legacy'),
        url(r'hpcapi/accessmaps/(?P<pk>[a-zA-Z0-9\-]+)/$', AccessMapDetail.as_view(), name ='accessmap-detail-legacy'),
    
        url(r'hpcapi/sitemaps/$', SiteMapList.as_view(), name='sitemap-list-legacy'),
        url(r'hpcapi/sitemaps/(?P<pk>[a-zA-Z0-9\-]+)/$', SiteMapDetail.as_view(), name ='sitemap-detail-legacy'),
    
    # new api - use these
        url(r'^api/service/hpc/$', hpc_api_root),
    
        url(r'api/service/hpc/hpchealthchecks/$', HpcHealthCheckList.as_view(), name='hpchealthcheck-list'),
        url(r'api/service/hpc/hpchealthchecks/(?P<pk>[a-zA-Z0-9\-]+)/$', HpcHealthCheckDetail.as_view(), name ='hpchealthcheck-detail'),
    
        url(r'api/service/hpc/hpcservices/$', HpcServiceList.as_view(), name='hpcservice-list'),
        url(r'api/service/hpc/hpcservices/(?P<pk>[a-zA-Z0-9\-]+)/$', HpcServiceDetail.as_view(), name ='hpcservice-detail'),
    
        url(r'api/service/hpc/originservers/$', OriginServerList.as_view(), name='originserver-list'),
        url(r'api/service/hpc/originservers/(?P<pk>[a-zA-Z0-9\-]+)/$', OriginServerDetail.as_view(), name ='originserver-detail'),
    
        url(r'api/service/hpc/cdnprefixs/$', CDNPrefixList.as_view(), name='cdnprefix-list'),
        url(r'api/service/hpc/cdnprefixs/(?P<pk>[a-zA-Z0-9\-]+)/$', CDNPrefixDetail.as_view(), name ='cdnprefix-detail'),
    
        url(r'api/service/hpc/serviceproviders/$', ServiceProviderList.as_view(), name='serviceprovider-list'),
        url(r'api/service/hpc/serviceproviders/(?P<pk>[a-zA-Z0-9\-]+)/$', ServiceProviderDetail.as_view(), name ='serviceprovider-detail'),
    
        url(r'api/service/hpc/contentproviders/$', ContentProviderList.as_view(), name='contentprovider-list'),
        url(r'api/service/hpc/contentproviders/(?P<pk>[a-zA-Z0-9\-]+)/$', ContentProviderDetail.as_view(), name ='contentprovider-detail'),
    
        url(r'api/service/hpc/accessmaps/$', AccessMapList.as_view(), name='accessmap-list'),
        url(r'api/service/hpc/accessmaps/(?P<pk>[a-zA-Z0-9\-]+)/$', AccessMapDetail.as_view(), name ='accessmap-detail'),
    
        url(r'api/service/hpc/sitemaps/$', SiteMapList.as_view(), name='sitemap-list'),
        url(r'api/service/hpc/sitemaps/(?P<pk>[a-zA-Z0-9\-]+)/$', SiteMapDetail.as_view(), name ='sitemap-detail'),
    
    )

@api_view(['GET'])
def hpc_api_root_legacy(request, format=None):
    return Response({
        'hpchealthchecks': reverse('hpchealthcheck-list-legacy', request=request, format=format),
        'hpcservices': reverse('hpcservice-list-legacy', request=request, format=format),
        'originservers': reverse('originserver-list-legacy', request=request, format=format),
        'cdnprefixs': reverse('cdnprefix-list-legacy', request=request, format=format),
        'serviceproviders': reverse('serviceprovider-list-legacy', request=request, format=format),
        'contentproviders': reverse('contentprovider-list-legacy', request=request, format=format),
        'accessmaps': reverse('accessmap-list-legacy', request=request, format=format),
        'sitemaps': reverse('sitemap-list-legacy', request=request, format=format),
        
    })

@api_view(['GET'])
def hpc_api_root(request, format=None):
    return Response({
        'hpchealthchecks': reverse('hpchealthcheck-list', request=request, format=format),
        'hpcservices': reverse('hpcservice-list', request=request, format=format),
        'originservers': reverse('originserver-list', request=request, format=format),
        'cdnprefixs': reverse('cdnprefix-list', request=request, format=format),
        'serviceproviders': reverse('serviceprovider-list', request=request, format=format),
        'contentproviders': reverse('contentprovider-list', request=request, format=format),
        'accessmaps': reverse('accessmap-list', request=request, format=format),
        'sitemaps': reverse('sitemap-list', request=request, format=format),
        
    })

# Based on serializers.py

class XOSModelSerializer(serializers.ModelSerializer):
    def save_object(self, obj, **kwargs):

        """ rest_framework can't deal with ManyToMany relations that have a
            through table. In xos, most of the through tables we have
            use defaults or blank fields, so there's no reason why we shouldn't
            be able to save these objects.

            So, let's strip out these m2m relations, and deal with them ourself.
        """
        obj._complex_m2m_data={};
        if getattr(obj, '_m2m_data', None):
            for relatedObject in obj._meta.get_all_related_many_to_many_objects():
                if (relatedObject.field.rel.through._meta.auto_created):
                    # These are non-trough ManyToMany relations and
                    # can be updated just fine
                    continue
                fieldName = relatedObject.get_accessor_name()
                if fieldName in obj._m2m_data.keys():
                    obj._complex_m2m_data[fieldName] = (relatedObject, obj._m2m_data[fieldName])
                    del obj._m2m_data[fieldName]

        serializers.ModelSerializer.save_object(self, obj, **kwargs);

        for (accessor, stuff) in obj._complex_m2m_data.items():
            (relatedObject, data) = stuff
            through = relatedObject.field.rel.through
            local_fieldName = relatedObject.field.m2m_reverse_field_name()
            remote_fieldName = relatedObject.field.m2m_field_name()

            # get the current set of existing relations
            existing = through.objects.filter(**{local_fieldName: obj});

            data_ids = [item.id for item in data]
            existing_ids = [getattr(item,remote_fieldName).id for item in existing]

            #print "data_ids", data_ids
            #print "existing_ids", existing_ids

            # remove relations that are in 'existing' but not in 'data'
            for item in list(existing):
               if (getattr(item,remote_fieldName).id not in data_ids):
                   print "delete", getattr(item,remote_fieldName)
                   item.delete() #(purge=True)

            # add relations that are in 'data' but not in 'existing'
            for item in data:
               if (item.id not in existing_ids):
                   #print "add", item
                   newModel = through(**{local_fieldName: obj, remote_fieldName: item})
                   newModel.save()



class HpcHealthCheckSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = HpcHealthCheck
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','hpcService','kind','resource_name','result_contains','result_min_size','result_max_size',)

class HpcHealthCheckIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = HpcHealthCheck
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','hpcService','kind','resource_name','result_contains','result_min_size','result_max_size',)




class HpcServiceSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = HpcService
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','description','enabled','kind','name','versionNumber','published','view_url','icon_url','public_key','private_key_fn','service_specific_id','service_specific_attribute','cmi_hostname','hpc_port80','watcher_hpc_network','watcher_dnsdemux_network','watcher_dnsredir_network',)

class HpcServiceIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = HpcService
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','description','enabled','kind','name','versionNumber','published','view_url','icon_url','public_key','private_key_fn','service_specific_id','service_specific_attribute','cmi_hostname','hpc_port80','watcher_hpc_network','watcher_dnsdemux_network','watcher_dnsredir_network',)




class OriginServerSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = OriginServer
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','origin_server_id','url','contentProvider','authenticated','enabled','protocol','redirects','description',)

class OriginServerIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = OriginServer
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','origin_server_id','url','contentProvider','authenticated','enabled','protocol','redirects','description',)




class CDNPrefixSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = CDNPrefix
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','cdn_prefix_id','prefix','contentProvider','description','defaultOriginServer','enabled',)

class CDNPrefixIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = CDNPrefix
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','cdn_prefix_id','prefix','contentProvider','description','defaultOriginServer','enabled',)




class ServiceProviderSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = ServiceProvider
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','hpcService','service_provider_id','name','description','enabled',)

class ServiceProviderIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = ServiceProvider
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','hpcService','service_provider_id','name','description','enabled',)




class ContentProviderSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = ContentProvider
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','content_provider_id','name','enabled','description','serviceProvider',)

class ContentProviderIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = ContentProvider
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','content_provider_id','name','enabled','description','serviceProvider',)




class AccessMapSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = AccessMap
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','contentProvider','name','description','map',)

class AccessMapIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = AccessMap
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','contentProvider','name','description','map',)




class SiteMapSerializer(serializers.HyperlinkedModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = SiteMap
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','contentProvider','serviceProvider','cdnPrefix','hpcService','name','description','map','map_id',)

class SiteMapIdSerializer(XOSModelSerializer):
    id = IdField()
    
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")
    validators = serializers.SerializerMethodField("getValidators")
    def getHumanReadableName(self, obj):
        return str(obj)
    def getValidators(self, obj):
        try:
            return obj.getValidators()
        except:
            return None
    class Meta:
        model = SiteMap
        fields = ('humanReadableName', 'validators', 'id','created','updated','enacted','policed','backend_register','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','contentProvider','serviceProvider','cdnPrefix','hpcService','name','description','map','map_id',)




serializerLookUp = {

                 HpcHealthCheck: HpcHealthCheckSerializer,

                 HpcService: HpcServiceSerializer,

                 OriginServer: OriginServerSerializer,

                 CDNPrefix: CDNPrefixSerializer,

                 ServiceProvider: ServiceProviderSerializer,

                 ContentProvider: ContentProviderSerializer,

                 AccessMap: AccessMapSerializer,

                 SiteMap: SiteMapSerializer,

                 None: None,
                }

# Based on core/views/*.py


class HpcHealthCheckList(XOSListCreateAPIView):
    queryset = HpcHealthCheck.objects.select_related().all()
    serializer_class = HpcHealthCheckSerializer
    id_serializer_class = HpcHealthCheckIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','hpcService','kind','resource_name','result_contains','result_min_size','result_max_size',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return HpcHealthCheck.select_by_user(self.request.user)


class HpcHealthCheckDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = HpcHealthCheck.objects.select_related().all()
    serializer_class = HpcHealthCheckSerializer
    id_serializer_class = HpcHealthCheckIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return HpcHealthCheck.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class HpcServiceList(XOSListCreateAPIView):
    queryset = HpcService.objects.select_related().all()
    serializer_class = HpcServiceSerializer
    id_serializer_class = HpcServiceIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','description','enabled','kind','name','versionNumber','published','view_url','icon_url','public_key','private_key_fn','service_specific_id','service_specific_attribute','cmi_hostname','hpc_port80','watcher_hpc_network','watcher_dnsdemux_network','watcher_dnsredir_network',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return HpcService.select_by_user(self.request.user)


class HpcServiceDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = HpcService.objects.select_related().all()
    serializer_class = HpcServiceSerializer
    id_serializer_class = HpcServiceIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return HpcService.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class OriginServerList(XOSListCreateAPIView):
    queryset = OriginServer.objects.select_related().all()
    serializer_class = OriginServerSerializer
    id_serializer_class = OriginServerIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','origin_server_id','url','contentProvider','authenticated','enabled','protocol','redirects','description',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return OriginServer.select_by_user(self.request.user)


class OriginServerDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = OriginServer.objects.select_related().all()
    serializer_class = OriginServerSerializer
    id_serializer_class = OriginServerIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return OriginServer.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class CDNPrefixList(XOSListCreateAPIView):
    queryset = CDNPrefix.objects.select_related().all()
    serializer_class = CDNPrefixSerializer
    id_serializer_class = CDNPrefixIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','cdn_prefix_id','prefix','contentProvider','description','defaultOriginServer','enabled',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return CDNPrefix.select_by_user(self.request.user)


class CDNPrefixDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = CDNPrefix.objects.select_related().all()
    serializer_class = CDNPrefixSerializer
    id_serializer_class = CDNPrefixIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return CDNPrefix.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class ServiceProviderList(XOSListCreateAPIView):
    queryset = ServiceProvider.objects.select_related().all()
    serializer_class = ServiceProviderSerializer
    id_serializer_class = ServiceProviderIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','hpcService','service_provider_id','name','description','enabled',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ServiceProvider.select_by_user(self.request.user)


class ServiceProviderDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = ServiceProvider.objects.select_related().all()
    serializer_class = ServiceProviderSerializer
    id_serializer_class = ServiceProviderIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ServiceProvider.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class ContentProviderList(XOSListCreateAPIView):
    queryset = ContentProvider.objects.select_related().all()
    serializer_class = ContentProviderSerializer
    id_serializer_class = ContentProviderIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','content_provider_id','name','enabled','description','serviceProvider',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ContentProvider.select_by_user(self.request.user)


class ContentProviderDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = ContentProvider.objects.select_related().all()
    serializer_class = ContentProviderSerializer
    id_serializer_class = ContentProviderIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return ContentProvider.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class AccessMapList(XOSListCreateAPIView):
    queryset = AccessMap.objects.select_related().all()
    serializer_class = AccessMapSerializer
    id_serializer_class = AccessMapIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','contentProvider','name','description','map',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return AccessMap.select_by_user(self.request.user)


class AccessMapDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = AccessMap.objects.select_related().all()
    serializer_class = AccessMapSerializer
    id_serializer_class = AccessMapIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return AccessMap.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView



class SiteMapList(XOSListCreateAPIView):
    queryset = SiteMap.objects.select_related().all()
    serializer_class = SiteMapSerializer
    id_serializer_class = SiteMapIdSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('id','created','updated','enacted','policed','backend_register','backend_status','deleted','write_protect','lazy_blocked','no_sync','no_policy','contentProvider','serviceProvider','cdnPrefix','hpcService','name','description','map','map_id',)

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return SiteMap.select_by_user(self.request.user)


class SiteMapDetail(XOSRetrieveUpdateDestroyAPIView):
    queryset = SiteMap.objects.select_related().all()
    serializer_class = SiteMapSerializer
    id_serializer_class = SiteMapIdSerializer

    def get_serializer_class(self):
        no_hyperlinks=False
        if hasattr(self.request,"query_params"):
            no_hyperlinks = self.request.query_params.get('no_hyperlinks', False)
        if (no_hyperlinks):
            return self.id_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        if (not self.request.user.is_authenticated()):
            raise XOSNotAuthenticated()
        return SiteMap.select_by_user(self.request.user)

    # update() is handled by XOSRetrieveUpdateDestroyAPIView

    # destroy() is handled by XOSRetrieveUpdateDestroyAPIView


