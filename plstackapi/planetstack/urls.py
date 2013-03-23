from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from core import views
from core.views import api_root
from core.models import Site
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
    url(r'^plstackapi/sites/$', views.SiteList.as_view(), name='site-list'),
    url(r'^plstackapi/sites/(?P<pk>[0-9]+)/$', views.SiteDetail.as_view(), name='site-detail'),

    url(r'^plstackapi/slices/$', views.SliceList.as_view(), name='slice-list'),
    url(r'^plstackapi/slices/(?P<pk>[0-9]+)/$', views.SliceDetail.as_view(), name='slice-detail'),

    url(r'^plstackapi/slivers/$', views.SliverList.as_view()),
    url(r'^plstackapi/slivers/(?P<pk>[0-9]+)/$', views.SliverDetail.as_view()),

    url(r'^plstackapi/nodes/$', views.NodeList.as_view(), name='node-list'),
    url(r'^plstackapi/nodes/(?P<pk>[0-9]+)/$', views.NodeDetail.as_view(), name='node-detail'),

    url(r'^plstackapi/deploymentnetworks/$', views.DeploymentNetworkList.as_view(), name='deploymentnetwork-list'),
    url(r'^plstackapi/deploymentnetworks/(?P<pk>[0-9]+)/$', views.DeploymentNetworkDetail.as_view(), name='deploymentnetwork-detail'),

    url(r'^plstackapi/sitedeploymentnetworks/$', views.SiteDeploymentNetworkList.as_view(), name='sitedeploymentnetwork-list'),
    url(r'^plstackapi/sitedeploymentnetworks/(?P<pk>[0-9]+)/$', views.SiteDeploymentNetworkDetail.as_view(), name='sitedeploymentnetwork-detail'),


    #Adding in rest_framework urls
    url(r'^plstackapi/', include('rest_framework.urls', namespace='rest_framework')),
    
)
