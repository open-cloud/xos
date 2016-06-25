import json
import os
import sys
import traceback
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework import status
from core.models import *
from xos.apibase import XOSListCreateAPIView, XOSRetrieveUpdateDestroyAPIView, XOSPermissionDenied
from api.xosapi_helpers import PlusModelSerializer, XOSViewSet, ReadOnlyField

# The Tosca engine expects to be run from /opt/xos/tosca/ or equivalent. It
# needs some sys.path fixing up.
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
toscadir = os.path.join(currentdir, "../../tosca")

class ToscaViewSet(XOSViewSet):
    base_name = "tosca"
    method_name = "tosca"
    method_kind = "viewset"

    @classmethod
    def get_urlpatterns(self, api_path="^"):
        patterns = []

        patterns.append( self.list_url("run/$", {"post": "post_run"}, "tosca_run") )

        return patterns

    def post_run(self, request):
        result = []

        recipe = request.data.get("recipe", None)

        sys_path_save = sys.path
        try:
            sys.path.append(toscadir)
            from tosca.engine import XOSTosca
            xt = XOSTosca(recipe, parent_dir=toscadir, log_to_console=False)
            xt.execute(request.user)
        except:
            return Response( {"error_text": traceback.format_exc()}, status=500 )
        finally:
            sys.path = sys_path_save


        return Response( {"log_msgs": xt.log_msgs} )







