# /opt/planetstack/core/dashboard/views/helloworld.py
import datetime
import os
import sys
import time
import json
from django.http import HttpResponse, HttpResponseServerError, HttpResponseForbidden
from django.views.generic import TemplateView, View
from django.forms.models import model_to_dict
from objects import XOSLIB_OBJECTS

class XOSLibDataView(View):
    def get(self, request,  name="hello_world", **kwargs):
        if name in XOSLIB_OBJECTS:
            result = XOSLIB_OBJECTS[name]().get()
        else:
            raise ValueError("Unknown object %s" % name)

        return HttpResponse(json.dumps(result), mimetype='application/json')
