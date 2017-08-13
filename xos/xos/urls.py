
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

from core.models import *
from rest_framework import generics
from django.http import HttpResponseRedirect

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

def redirect_to_apache(request):
    """ bounce a request back to the apache server that is running on the machine """
    apache_url = "http://%s%s" % (request.META['HOSTNAME'], request.path)
    return HttpResponseRedirect(apache_url)

urlpatterns = patterns(
    '',
    # Is this necessary?
    url(r'^files/', redirect_to_apache),

    # Adding in rest_framework urls
    url(r'^xos/', include('rest_framework.urls', namespace='rest_framework')),

    # handcrafted API methods
    # NOTE: Needs to stay until Tosca switchover is complete
    url(r'^', include('api.import_methods', namespace='api')),
  )

