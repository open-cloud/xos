from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from core.views.deployments import DeploymentList, DeploymentDetail
from core.views.images import ImageList, ImageDetail
from core.views.nodes import NodeList, NodeDetail
from core.views.projects import ProjectList, ProjectDetail
from core.views.reservations import ReservationList, ReservationDetail
from core.views.roles import RoleList, RoleDetail
from core.views.serviceclasses import ServiceClassList, ServiceClassDetail
from core.views.serviceresources import ServiceResourceList, ServiceResourceDetail
from core.views.sites import SiteList, SiteDetail
from core.views.site_privileges import SitePrivilegeList, SitePrivilegeDetail
from core.views.slices import SliceList, SliceDetail
from core.views.slice_privileges import SlicePrivilegeList, SlicePrivilegeDetail
from core.views.slivers import SliverList, SliverDetail
from core.views.tags import TagList, TagDetail
from genapi import UserList, UserDetail
from core.views.legacyapi import LegacyXMLRPC
from core.models import *
from core.api_root import api_root
from rest_framework import generics
from core.plus.sites import SitePlus

admin.site = SitePlus()
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'planetstack.views.home', name='home'),
    # url(r'^planetstack/', include('planetstack.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include(admin.site.urls)),
    #url(r'^profile/home', 'core.views.home'),

    url(r'^plstackapi/$', api_root),
    
    url(r'^plstackapi/deployments/$', DeploymentList.as_view(), name='deployment-list'),
    url(r'^plstackapi/deployments/(?P<pk>[a-zA-Z0-9\-]+)/$', DeploymentDetail.as_view(), name='deployment-detail'),

    url(r'^plstackapi/images/$', ImageList.as_view(), name='image-list'),
    url(r'^plstackapi/images/(?P<pk>[a-zA-Z0-9_\-]+)/$', ImageDetail.as_view(), name='image-detail'),

    url(r'^plstackapi/nodes/$', NodeList.as_view(), name='node-list'),
    url(r'^plstackapi/nodes/(?P<pk>[a-zA-Z0-9_\-]+)/$', NodeDetail.as_view(), name='node-detail'),
    
    url(r'^plstackapi/projects/$', ProjectList.as_view(), name='project-list'),
    url(r'^plstackapi/projects/(?P<pk>[a-zA-Z0-9_\-]+)/$', ProjectDetail.as_view(), name='project-detail'),
    
    url(r'^plstackapi/reservations/$', ReservationList.as_view(), name='reservation-list'),
    url(r'^plstackapi/reservations/(?P<pk>[a-zA-Z0-9_\-]+)/$', ReservationDetail.as_view(), name='reservation-detail'),
    
    url(r'^plstackapi/roles/$', RoleList.as_view(), name='role-list'),
    url(r'^plstackapi/roles/(?P<pk>[a-zA-Z0-9]+)/$', RoleDetail.as_view(), name='role-detail'),

    url(r'^plstackapi/serviceclasses/$', ServiceClassList.as_view(), name='serviceclass-list'),
    url(r'^plstackapi/serviceclasses/(?P<pk>[a-zA-Z0-9]+)/$', ServiceClassDetail.as_view(), name='serviceclass-detail'),

    url(r'^plstackapi/serviceresources/$', ServiceResourceList.as_view(), name='serviceresource-list'),
    url(r'^plstackapi/serviceresources/(?P<pk>[a-zA-Z0-9]+)/$', ServiceResourceDetail.as_view(), name='serviceresource-detail'),

    url(r'^plstackapi/site_privileges/$', SitePrivilegeList.as_view(), name='siteprivilege-list'),
    url(r'^plstackapi/site_privileges/(?P<pk>[a-zA-Z0-9_]+)/$', SitePrivilegeDetail.as_view(), name='siteprivilege-detail'),
  
    url(r'^plstackapi/sites/$', SiteList.as_view(), name='site-list'),
    url(r'^plstackapi/sites/(?P<pk>[a-zA-Z0-9_\-]+)/$', SiteDetail.as_view(), name='site-detail'),

    url(r'^plstackapi/slices/$', SliceList.as_view(), name='slice-list'),

    url(r'^plstackapi/slices/(?P<pk>[a-zA-Z0-9_\-]+)/$', SliceDetail.as_view(), name='slice-detail'),

    url(r'^plstackapi/slice_memberships/$', SlicePrivilegeList.as_view(), name='sliceprivilege-list'),
    url(r'^plstackapi/slice_memberships/(?P<pk>[0-9]+)/$', SlicePrivilegeDetail.as_view(), name='sliceprivilege-detail'),
    
    url(r'^plstackapi/slivers/$', SliverList.as_view(), name='sliver-list'),
    url(r'^plstackapi/slivers/(?P<pk>[a-zA-Z0-9_\-]+)/$', SliverDetail.as_view(), name='sliver-detail'),

    url(r'^plstackapi/tags/$', TagList.as_view(), name='tag-list'),
    url(r'^plstackapi/tags/(?P<pk>[a-zA-Z0-9_\-]+)/$', TagDetail.as_view(), name='tag-detail'),

    url(r'^plstackapi/users/$', UserList.as_view(), name='user-list'),
    url(r'^plstackapi/users/(?P<pk>[a-zA-Z0-9_\-]+)/$', UserDetail.as_view(), name='user-detail'),

    url(r'^legacyapi/$', 'core.views.legacyapi.LegacyXMLRPC', name='xmlrpc'),


    #Adding in rest_framework urls
    url(r'^plstackapi/', include('rest_framework.urls', namespace='rest_framework')),
    
)
