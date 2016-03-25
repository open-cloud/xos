from django.views.generic import View
from django.conf.urls import patterns, url
from rest_framework.routers import DefaultRouter
import os, sys
import inspect
import importlib

def import_module_from_filename(pathname):
    sys_path_save = sys.path
    try:
        # __import__() and importlib.import_module() both import modules from
        # sys.path. So we make sure that the path where we can find the views is
        # the first thing in sys.path.
        sys.path = [dir] + sys.path

        module = __import__(fn[:-3])
    finally:
        sys.path = sys_path_save

    return module

def import_methods(dir=None, api_path="api"):
    urlpatterns=[]
    subdirs=[]

    if not dir:
        dir = os.path.dirname(os.path.abspath(__file__))

    for fn in os.listdir(dir):
        pathname = os.path.join(dir,fn)
        if os.path.isfile(pathname) and fn.endswith(".py") and (fn!="__init__.py"):
            module = import_module_from_filename(fn[:-3])
            for classname in dir(module):
                c = getattr(module, classname, None)

                if inspect.isclass(c) and issubclass(c, View) and (classname not in globals()):
                    globals()[classname] = c

                    method_kind = getattr(c, "method_kind", None)
                    method_name = os.path.join(api_path, getattr(c, "method_name", None))
                    if method_kind and method_name:
                        view_urls.append( (method_kind, method_name, classname, c) )

        elif os.path.isdir(pathname):
            urlpatterns.extend(import_methods(os.path.append(dir, fn), os.path.append(api_path, fn)))

    for view_url in view_urls:
        if view_url[0] == "list":
           urlpatterns.append(url(r'^' + view_url[1] + '/$',  view_url[3].as_view(), name=view_url[1]+'list'))
        elif view_url[0] == "detail":
           urlpatterns.append(url(r'^' + view_url[1] + '/(?P<pk>[a-zA-Z0-9\-]+)/$',  view_url[3].as_view(), name=view_url[1]+'detail'))
        elif view_url[0] == "viewset":
           viewset = view_url[3]

           urlpatterns.extend(viewset.get_urlpatterns())

    return urlpatterns
