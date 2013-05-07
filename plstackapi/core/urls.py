from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from plstackapi.core.views.roles import RoleListCreate, RoleRetrieveUpdateDestroy
from plstackapi.core.views.sites import SiteListCreate, SiteRetrieveUpdateDestroy
from plstackapi.core.views.site_privileges import SitePrivilegeListCreate, SitePrivilegeRetrieveUpdateDestroy
from plstackapi.core.views.users import UserListCreate, UserRetrieveUpdateDestroy
from plstackapi.core.views.slices import SliceListCreate, SliceRetrieveUpdateDestroy
from plstackapi.core.views.slice_memberships import SliceMembershipListCreate, SliceMembershipRetrieveUpdateDestroy
from plstackapi.core.views.slivers import SliverListCreate, SliverRetrieveUpdateDestroy
from plstackapi.core.views.keys import KeyListCreate, KeyRetrieveUpdateDestroy
from plstackapi.core.views.deployment_networks import DeploymentNetworkListCreate, DeploymentNetworkRetrieveUpdateDestroy
from plstackapi.core.views.images import ImageListCreate, ImageRetrieveUpdateDestroy
from plstackapi.core.views.nodes import NodeListCreate, NodeRetrieveUpdateDestroy
from plstackapi.core.models import Site
from plstackapi.core.api_root import api_root
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
    url(r'^plstackapi/users/(?P<pk>[a-zA-Z0-9_\-]+)/$', UserRetrieveUpdateDestroy.as_view(), name='user-detail'),

    url(r'^plstackapi/keys/$', KeyListCreate.as_view(), name='key-list'),
    url(r'^plstackapi/keys/(?P<pk>[a-zA-Z0-9_\-]+)/$', KeyRetrieveUpdateDestroy.as_view(), name='key-detail'),

    url(r'^plstackapi/sites/$', SiteListCreate.as_view(), name='site-list'),
    url(r'^plstackapi/sites/(?P<pk>[a-zA-Z0-9_\-]+)/$', SiteRetrieveUpdateDestroy.as_view(), name='site-detail'),

    url(r'^plstackapi/site_privileges/$', SitePrivilegeListCreate.as_view(), name='siteprivilege-list'),
    url(r'^plstackapi/site_privileges/(?P<pk>[a-zA-Z0-9_]+)/$', SitePrivilegeRetrieveUpdateDestroy.as_view(), name='siteprivilege-detail'),

    url(r'^plstackapi/slices/$', SliceListCreate.as_view(), name='slice-list'),
    url(r'^plstackapi/slices/(?P<pk>[a-zA-Z0-9_\-]+)/$', SliceRetrieveUpdateDestroy.as_view(), name='slice-detail'),

    url(r'^plstackapi/slice_memberships/$', SliceMembershipListCreate.as_view(), name='slice_membership-list'),
    url(r'^plstackapi/slice_memberships/(?P<pk>[0-9]+)/$', SliceMembershipRetrieveUpdateDestroy.as_view(), name='slice_membership-detail'),
    
    url(r'^plstackapi/slivers/$', SliverListCreate.as_view(), name='sliver-list'),
    url(r'^plstackapi/slivers/(?P<pk>[a-zA-Z0-9_\-]+)/$', SliverRetrieveUpdateDestroy.as_view(), name='sliver-detail'),

    url(r'^plstackapi/nodes/$', NodeListCreate.as_view(), name='node-list'),
    url(r'^plstackapi/nodes/(?P<pk>[a-zA-Z0-9_\-]+)/$', NodeRetrieveUpdateDestroy.as_view(), name='node-detail'),
    
    url(r'^plstackapi/deploymentnetworks/$', DeploymentNetworkListCreate.as_view(), name='deploymentnetwork-list'),
    url(r'^plstackapi/deploymentnetworks/(?P<pk>[a-zA-Z0-9\-]+)/$', DeploymentNetworkRetrieveUpdateDestroy.as_view(), name='deploymentnetwork-detail'),

    url(r'^plstackapi/images/$', ImageListCreate.as_view(), name='image-list'),
    url(r'^plstackapi/images/(?P<pk>[a-zA-Z0-9_\-]+)/$', ImageRetrieveUpdateDestroy.as_view(), name='image-detail'),

    #Adding in rest_framework urls
    url(r'^plstackapi/', include('rest_framework.urls', namespace='rest_framework')),
    
)
