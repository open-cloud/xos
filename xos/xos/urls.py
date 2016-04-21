from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

# This is the generated API
from xosapi import *
from hpcapi import *

from core.views.legacyapi import LegacyXMLRPC
from core.views.serviceGraph import ServiceGridView, ServiceGraphView
from core.models import *
from rest_framework import generics
from core.dashboard.sites import SitePlus
from django.http import HttpResponseRedirect
#from api import import_api_methods

admin.site = SitePlus()
admin.autodiscover()

def redirect_to_apache(request):
     """ bounce a request back to the apache server that is running on the machine """
     apache_url = "http://%s%s" % (request.META['HOSTNAME'], request.path)
     return HttpResponseRedirect(apache_url)

urlpatterns = patterns('',
    # Examples:
    url(r'^observer', 'core.views.observer.Observer', name='observer'),
    url(r'^serviceGrid', ServiceGridView.as_view(), name='serviceGrid'),
    url(r'^serviceGraph.png', ServiceGraphView.as_view(), name='serviceGraph'),
    url(r'^hpcConfig', 'core.views.hpc_config.HpcConfig', name='hpcConfig'),

    url(r'^docs/', include('rest_framework_swagger.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include(admin.site.urls)),
    #url(r'^profile/home', 'core.views.home'),

    url(r'^xmlrpc/legacyapi/$', 'core.views.legacyapi.LegacyXMLRPC', name='xmlrpc'),

    url(r'^files/', redirect_to_apache),

    # Adding in rest_framework urls
    url(r'^xos/', include('rest_framework.urls', namespace='rest_framework')),

    # XOSLib rest methods [deprecated]
    url(r'^xoslib/', include('core.xoslib.methods', namespace='xoslib')),

    url(r'^', include('api.import_methods', namespace='api')),

  ) + get_REST_patterns() + get_hpc_REST_patterns()

