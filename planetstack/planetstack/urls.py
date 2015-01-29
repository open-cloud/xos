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
    url(r'^stats', 'core.views.stats.Stats', name='stats'),
    url(r'^observer', 'core.views.observer.Observer', name='observer'),


    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include(admin.site.urls)),
    #url(r'^profile/home', 'core.views.home'),

#    url(r'^admin/xoslib/(?P<name>\w+)/$', XOSLibDataView.as_view(), name="xoslib"),

    url(r'^xmlrpc/legacyapi/$', 'core.views.legacyapi.LegacyXMLRPC', name='xmlrpc'),

#    url(r'^analytics/(?P<name>\w+)/$', AnalyticsAjaxView.as_view(), name="analytics"),

    url(r'^files/', redirect_to_apache),

    #Adding in rest_framework urls
    url(r'^plstackapi/', include('rest_framework.urls', namespace='rest_framework')),

    # XOSLib rest methods
    url(r'^xoslib/', include('core.xoslib.methods', namespace='xoslib')),
  ) + get_REST_patterns()

