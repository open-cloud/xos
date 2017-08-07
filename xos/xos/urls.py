
# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import importlib
from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

# This is the generated API
from xosapi import *

# from services.vbbu.view import *
from core.views.mcordview import *
# from core.views.analytics import AnalyticsAjaxView

from core.models import *
from rest_framework import generics
from core.dashboard.sites import SitePlus
from django.http import HttpResponseRedirect

# from core.xoslib import XOSLibDataView

def load_class(full_class_string):
    """
    dynamically load a class from a string
    """

    class_data = full_class_string.split(".")
    module_path = ".".join(class_data[:-1])
    class_str = class_data[-1]

    module = importlib.import_module(module_path)
    # Finally, we retrieve the Class
    return getattr(module, class_str)

# from api import import_api_methods

admin.site = SitePlus()
admin.autodiscover()


def redirect_to_apache(request):
    """ bounce a request back to the apache server that is running on the machine """
    apache_url = "http://%s%s" % (request.META['HOSTNAME'], request.path)
    return HttpResponseRedirect(apache_url)

urlpatterns = patterns(
    '',

    # url(r'^docs/', include('rest_framework_swagger.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include(admin.site.urls)),
    # url(r'^profile/home', 'core.views.home'),

    # url(r'^admin/xoslib/(?P<name>\w+)/$', XOSLibDataView.as_view(), name="xoslib"),

    # url(r'^analytics/(?P<name>\w+)/$', AnalyticsAjaxView.as_view(), name="analytics"),

    url(r'^files/', redirect_to_apache),

    # Adding in rest_framework urls
    url(r'^xos/', include('rest_framework.urls', namespace='rest_framework')),

    # XOSLib rest methods [deprecated]
    url(r'^xoslib/', include('core.xoslib.methods', namespace='xoslib')),

    url(r'^', include('api.import_methods', namespace='api')),

  ) + get_REST_patterns()
