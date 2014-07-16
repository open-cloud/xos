from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

# This is the generated API
from genapi import *

from core.views.legacyapi import LegacyXMLRPC
#from core.views.analytics import AnalyticsAjaxView
from core.models import *
from rest_framework import generics
from core.dashboard.sites import SitePlus
from django.http import HttpResponseRedirect
#from core.xoslib import XOSLibDataView

admin.site = SitePlus()
admin.autodiscover()

def redirect_to_apache(request):
     """ bounce a request back to the apache server that is running on the machine """
     apache_url = "http://%s%s" % (request.META['HOSTNAME'], request.path)
     return HttpResponseRedirect(apache_url)

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

#    url(r'^admin/xoslib/(?P<name>\w+)/$', XOSLibDataView.as_view(), name="xoslib"),

    url(r'^plstackapi/$', api_root),

    url(r'^plstackapi/dashboardviews/$', DashboardViewList.as_view(), name='dashboardview-list'),
    url(r'^plstackapi/dashboardview/(?P<pk>[a-zA-Z0-9\-]+)/$', DashboardViewDetail.as_view(), name='dashboardview-detail'),

    url(r'^plstackapi/payments/$', PaymentList.as_view(), name='payment-list'),
    url(r'^plstackapi/payments/(?P<pk>[a-zA-Z0-9\-]+)/$', PaymentDetail.as_view(), name='payment-detail'),

    url(r'^plstackapi/charges/$', ChargeList.as_view(), name='charge-list'),
    url(r'^plstackapi/charges/(?P<pk>[a-zA-Z0-9\-]+)/$', ChargeDetail.as_view(), name='charge-detail'),

    url(r'^plstackapi/accounts/$', AccountList.as_view(), name='account-list'),
    url(r'^plstackapi/accounts/(?P<pk>[a-zA-Z0-9\-]+)/$', AccountDetail.as_view(), name='account-detail'),

    url(r'^plstackapi/deployments/$', DeploymentList.as_view(), name='deployment-list'),
    url(r'^plstackapi/deployments/(?P<pk>[a-zA-Z0-9\-]+)/$', DeploymentDetail.as_view(), name='deployment-detail'),

    url(r'^plstackapi/images/$', ImageList.as_view(), name='image-list'),
    url(r'^plstackapi/images/(?P<pk>[a-zA-Z0-9_\-]+)/$', ImageDetail.as_view(), name='image-detail'),

    url(r'^plstackapi/networkparametertypes/$', NodeList.as_view(), name='node-list'),
    url(r'^plstackapi/networkparametertypes/(?P<pk>[a-zA-Z0-9_\-]+)/$', NodeDetail.as_view(), name='node-detail'),

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

    url(r'^plstackapi/accounts/$', AccountList.as_view(), name='account-list'),
    url(r'^plstackapi/accounts/(?P<pk>[a-zA-Z0-9_\-]+)/$', AccountDetail.as_view(), name='account-detail'),

    url(r'^plstackapi/networktemplates/$', NetworkSliceList.as_view(), name='networkslice-list'),
    url(r'^plstackapi/networktemplates/(?P<pk>[a-zA-Z0-9_\-]+)/$', NetworkSliceDetail.as_view(), name='networkslice-detail'),

    url(r'^plstackapi/networkslices/$', NetworkSliceList.as_view(), name='networkslice-list'),
    url(r'^plstackapi/networkslices/(?P<pk>[a-zA-Z0-9_\-]+)/$', NetworkSliceDetail.as_view(), name='networkslice-detail'),

    url(r'^plstackapi/networks/$', NetworkList.as_view(), name='network-list'),
    url(r'^plstackapi/networks/(?P<pk>[a-zA-Z0-9_\-]+)/$', NetworkDetail.as_view(), name='network-detail'),
    
    url(r'^plstackapi/services/$', SliceList.as_view(), name='service-list'),
    url(r'^plstackapi/services/(?P<pk>[a-zA-Z0-9_\-]+)/$', SliceDetail.as_view(), name='service-detail'),

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

#    url(r'^analytics/(?P<name>\w+)/$', AnalyticsAjaxView.as_view(), name="analytics"),

    url(r'^files/', redirect_to_apache),

    #Adding in rest_framework urls
    url(r'^plstackapi/', include('rest_framework.urls', namespace='rest_framework')),

    # XOSLib rest methods
    url(r'^xoslib/', include('core.xoslib.methods', namespace='xoslib')),    
)
