from django.views.generic import View
from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter
import os, sys
import inspect
import importlib

urlpatterns = []

def import_module_from_filename(dirname, fn):
    sys_path_save = sys.path
    try:
        # __import__() and importlib.import_module() both import modules from
        # sys.path. So we make sure that the path where we can find the views is
        # the first thing in sys.path.
        sys.path = [dirname] + sys.path

        module = __import__(fn[:-3])
    finally:
        sys.path = sys_path_save

    return module

def import_api_methods(dirname=None, api_path="api"):
    subdirs=[]
    urlpatterns=[]

    if not dirname:
        dirname = os.path.dirname(os.path.abspath(__file__))

    view_urls = []
    for fn in os.listdir(dirname):
        pathname = os.path.join(dirname,fn)
        if os.path.isfile(pathname) and fn.endswith(".py") and (fn!="__init__.py"):
            module = import_module_from_filename(dirname, fn)
            for classname in dir(module):
                c = getattr(module, classname, None)

                if inspect.isclass(c) and issubclass(c, View) and (classname not in globals()):
                    globals()[classname] = c

                    method_kind = getattr(c, "method_kind", None)
                    method_name = getattr(c, "method_name", None)
                    if method_kind and method_name:
                        method_name = os.path.join(api_path, method_name)
                        view_urls.append( (method_kind, method_name, classname, c) )

        elif os.path.isdir(pathname):
            urlpatterns.extend(import_api_methods(pathname, os.path.join(api_path, fn)))

    for view_url in view_urls:
        if view_url[0] == "list":
           urlpatterns.append(url(r'^' + view_url[1] + '/$',  view_url[3].as_view(), name=view_url[1]+'list'))
        elif view_url[0] == "detail":
           urlpatterns.append(url(r'^' + view_url[1] + '/(?P<pk>[a-zA-Z0-9\-]+)/$',  view_url[3].as_view(), name=view_url[1]+'detail'))
        elif view_url[0] == "viewset":
           viewset = view_url[3]
           urlpatterns.extend(viewset.get_urlpatterns(api_path=api_path+"/"))

    return urlpatterns

urlpatterns = import_api_methods()

