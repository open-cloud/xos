
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


#from home import DashboardWelcomeView, DashboardDynamicView
#from tenant import TenantCreateSlice, TenantUpdateSlice, TenantDeleteSliceView, TenantAddOrRemoveInstanceView, TenantPickSitesView, TenantViewData
#from simulator import SimulatorView
#from cdn import DashboardSummaryAjaxView, DashboardAddOrRemoveInstanceView, DashboardAjaxView
#from analytics import DashboardAnalyticsAjaxView
#from interactions import DashboardSliceInteractions
#from test import DashboardUserSiteView

from django.views.generic import View
from django.conf.urls import patterns, url
import os, sys
import inspect
import importlib

# Find all modules in the current directory that have descendents of the View
# object, and add them as globals to this module. Also, build up a list of urls
# based on the "url" field of the view classes.

sys_path_save = sys.path
try:
    # __import__() and importlib.import_module() both import modules from
    # sys.path. So we make sure that the path where we can find the views is
    # the first thing in sys.path.
    view_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path = [view_dir] + sys.path
    view_urls = []
    for fn in os.listdir(view_dir):
        pathname = os.path.join(view_dir,fn)
        if os.path.isfile(pathname) and fn.endswith(".py") and (fn!="__init__.py"):
            #module = imp.load_source(fn[:-3],pathname)
            #module = importlib.import_module(fn[:-3])
            module = __import__(fn[:-3])
            for classname in dir(module):
                c = getattr(module, classname, None)

                if inspect.isclass(c) and issubclass(c, View) and (classname not in globals()):
                    globals()[classname] = c

                    view_url = getattr(c, "url", None)
                    if view_url:
                        view_urls.append( (view_url, classname, c) )
finally:
    sys.path = sys_path_save
