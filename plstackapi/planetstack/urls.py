from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from plstackapi.planetstack.api_root import api_root
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
    
    #Adding in rest_framework urls
    url(r'^plstackapi/', include('rest_framework.urls', namespace='rest_framework')),
    
)
