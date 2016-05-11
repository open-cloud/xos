from django.views.generic import View
from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter
from xosapi_helpers import XOSIndexViewSet
import os, sys
import inspect
import importlib

try:
    from rest_framework.serializers import DictField
except:
    raise Exception("Failed check for django-rest-framework >= 3.3.3")

urlpatterns = []

def import_module_from_filename(dirname, fn):
    print "importing", dirname, fn
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

def import_module_by_dotted_name(name):
    print "import", name
    try:
        module = __import__(name)
    except:
        # django will eat the exception, and then fail later with
        #  'conflicting models in application'
        # when it tries to import the module a second time.
        print "exception in import_model_by_dotted_name"
        import traceback
        traceback.print_exc()
        raise
    for part in name.split(".")[1:]:
        module = getattr(module, part)
    return module

def import_api_methods(dirname=None, api_path="api", api_module="api"):
    has_index_view = False
    subdirs=[]
    urlpatterns=[]

    if not dirname:
        dirname = os.path.dirname(os.path.abspath(__file__))

    view_urls = []
    for fn in os.listdir(dirname):
        pathname = os.path.join(dirname,fn)
        if os.path.isfile(pathname) and fn.endswith(".py") and (fn!="__init__.py") and (fn!="import_methods.py"):
            #module = import_module_from_filename(dirname, fn)
            module = import_module_by_dotted_name(api_module + "." + fn[:-3])
            for classname in dir(module):
#                print "  ",classname
                c = getattr(module, classname, None)

                if inspect.isclass(c) and issubclass(c, View) and (classname not in globals()):
                    globals()[classname] = c

                    method_kind = getattr(c, "method_kind", None)
                    method_name = getattr(c, "method_name", None)
                    if method_kind:
                        if method_name:
                            method_name = os.path.join(api_path, method_name)
                        else:
                            method_name = api_path
                            has_index_view = True
                        view_urls.append( (method_kind, method_name, classname, c) )

        elif os.path.isdir(pathname):
            urlpatterns.extend(import_api_methods(pathname, os.path.join(api_path, fn), api_module+"." + fn))
            subdirs.append(fn)

    for view_url in view_urls:
        if view_url[0] == "list":
           urlpatterns.append(url(r'^' + view_url[1] + '/$',  view_url[3].as_view(), name=view_url[1]+'list'))
        elif view_url[0] == "detail":
           urlpatterns.append(url(r'^' + view_url[1] + '/(?P<pk>[a-zA-Z0-9\-]+)/$',  view_url[3].as_view(), name=view_url[1]+'detail'))
        elif view_url[0] == "viewset":
           viewset = view_url[3]
           urlpatterns.extend(viewset.get_urlpatterns(api_path="^"+api_path+"/"))

    # Only add an index_view if 1) the is not already an index view, and
    # 2) we have found some methods in this directory.
    if (not has_index_view) and (urlpatterns):
        # The browseable API uses the classname as the breadcrumb and page
        # title, so try to create index views with descriptive classnames
        viewset = type("IndexOf"+api_path.split("/")[-1].title(), (XOSIndexViewSet,), {})
        urlpatterns.append(url('^' + api_path + '/$', viewset.as_view({'get': 'list'}, view_urls=view_urls, subdirs=subdirs, api_path=api_path), name=api_path+"_index"))

    return urlpatterns

urlpatterns = import_api_methods()

