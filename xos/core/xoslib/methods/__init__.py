from django.views.generic import View
from django.conf.urls import patterns, url
from rest_framework.routers import DefaultRouter
import os, sys
import inspect
import importlib

# XXX based on core/dashboard/views/__init__.py

# Find all modules in the current directory that have descendents of the View
# object, and add them as globals to this module. Also, build up a list of urls
# based on the "url" field of the view classes.

urlpatterns=[]

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

                if inspect.isclass(c) and issubclass(c, View) and (classname not in globals()):
                    globals()[classname] = c

                    method_kind = getattr(c, "method_kind", None)
                    method_name = getattr(c, "method_name", None)
                    if method_kind and method_name:
                        view_urls.append( (method_kind, method_name, classname, c) )

    for view_url in view_urls:
        if view_url[0] == "list":
           urlpatterns.append(url(r'^' + view_url[1] + '/$',  view_url[3].as_view(), name=view_url[1]+'list'))
        elif view_url[0] == "detail":
           urlpatterns.append(url(r'^' + view_url[1] + '/(?P<pk>[a-zA-Z0-9\-]+)/$',  view_url[3].as_view(), name=view_url[1]+'detail'))
        elif view_url[0] == "viewset":
           viewset = view_url[3]

           urlpatterns.extend(viewset.get_urlpatterns())

           #urlpatterns.append(url(r'^' + view_url[1] + '/$', viewset.as_view({'get': 'list'}), name=view_url[1]+'list'))
           #urlpatterns.append(url(r'^' + view_url[1] + '/(?P<pk>[a-zA-Z0-9\-]+)/$', viewset.as_view({'get': 'retrieve', 'put': 'update', 'post': 'create', 'delete': 'destroy', 'patch': 'partial_update'}), name=view_url[1]+'detail'))
           #urlpatterns.extend(

           #router = DefaultRouter()
           #router.register(r'^' + view_url[1], view_url[3], base_name="foo")
           #urlpatterns.extend(router.urls)
           #urlpatterns.append(url(r'^' + view_url[1], view_url[3]))

finally:
    sys.path = sys_path_save
