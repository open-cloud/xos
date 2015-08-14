from xosresource import XOSResource
from django.conf.urls import patterns, url
from rest_framework.routers import DefaultRouter
import os, sys
import inspect
import importlib

# XXX based on core/dashboard/views/__init__.py

# Find all modules in the current directory that have descendents of the XOSResource
# object, and add them as globals to this module. Also, build up a list of urls
# based on the "url" field of the view classes.

resources = {}

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
            module = __import__(fn[:-3])
            for classname in dir(module):
                c = getattr(module, classname, None)

                if inspect.isclass(c) and (getattr(c,"xos_base_class",None)=="XOSResource") and (classname not in globals()):
                    provides = getattr(c, "provides", None)
                    if provides:
                        globals()[classname] = c
                        if isinstance(provides, basestring):
                            resources[provides] = c
                        else:
                            # allow provides= to be a list
                            for p in provides:
                                resources[p] = c
finally:
    sys.path = sys_path_save
