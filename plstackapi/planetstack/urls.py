from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from plstackapi.planetstack.views.roles import RoleListCreate, RoleRetrieveUpdateDestroy
from plstackapi.planetstack.views.sites import SiteListCreate, SiteRetrieveUpdateDestroy
from plstackapi.planetstack.views.users import UserListCreate, UserRetrieveUpdateDestroy
from plstackapi.planetstack.views.deployment_networks import DeploymentNetworkListCreate, DeploymentNetworkRetrieveUpdateDestroy
from plstackapi.planetstack.views.images import ImageListCreate, ImageRetrieveUpdateDestroy
from plstackapi.planetstack.views.flavors import FlavorListCreate, FlavorRetrieveUpdateDestroy
from plstackapi.planetstack.views.api_root import api_root
from plstackapi.planetstack.models import Site
from rest_framework import generics

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'planetstack.views.home', name='home'),
    # url(r'^planetstack/', include('planetstack.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^plstackapi/$', api_root),
    
    url(r'^plstackapi/roles/$', RoleListCreate.as_view(), name='role-list'),
    url(r'^plstackapi/roles/(?P<pk>[a-zA-Z0-9]+)/$', RoleRetrieveUpdateDestroy.as_view(), name='role-detail'),

    url(r'^plstackapi/users/$', UserListCreate.as_view(), name='user-list'),
    url(r'^plstackapi/users/(?P<pk>[a-zA-Z0-9]+)/$', UserRetrieveUpdateDestroy.as_view(), name='user-detail'),

    url(r'^plstackapi/sites/$', SiteListCreate.as_view(), name='site-list'),
    url(r'^plstackapi/sites/(?P<pk>[a-zA-Z0-9_]+)/$', SiteRetrieveUpdateDestroy.as_view(), name='site-detail'),

    #url(r'^plstackapi/slices/$', views.SliceList.as_view(), name='slice-list'),
    #url(r'^plstackapi/slices/(?P<pk>[0-9]+)/$', views.SliceDetail.as_view(), name='slice-detail'),

    #url(r'^plstackapi/slivers/$', views.SliverList.as_view()),
    #url(r'^plstackapi/slivers/(?P<pk>[0-9]+)/$', views.SliverDetail.as_view()),

    #url(r'^plstackapi/nodes/$', views.NodeList.as_view(), name='node-list'),
    #url(r'^plstackapi/nodes/(?P<pk>[0-9]+)/$', views.NodeDetail.as_view(), name='node-detail'),

    
    url(r'^plstackapi/deploymentnetworks/$', DeploymentNetworkListCreate.as_view(), name='deploymentnetwork-list'),
    url(r'^plstackapi/deploymentnetworks/(?P<pk>[a-zA-Z0-9]+)/$', DeploymentNetworkRetrieveUpdateDestroy.as_view(), name='deploymentnetwork-detail'),

    #url(r'^plstackapi/sitedeploymentnetworks/$', views.SiteDeploymentNetworkList.as_view(), name='sitedeploymentnetwork-list'),
    #url(r'^plstackapi/sitedeploymentnetworks/(?P<pk>[0-9]+)/$', views.SiteDeploymentNetworkDetail.as_view(), name='sitedeploymentnetwork-detail'),

    url(r'^plstackapi/images/$', ImageListCreate.as_view(), name='image-list'),
    url(r'^plstackapi/images/(?P<pk>[a-zA-Z0-9_]+)/$', ImageRetrieveUpdateDestroy.as_view(), name='image-detail'),

    url(r'^plstackapi/flavors/$', FlavorListCreate.as_view(), name='flavor-list'),
    url(r'^plstackapi/flavors/(?P<pk>[a-zA-Z0-9_]+)/$', FlavorRetrieveUpdateDestroy.as_view(), name='flavor-detail'),
    #Adding in rest_framework urls
    url(r'^plstackapi/', include('rest_framework.urls', namespace='rest_framework')),
    
)
