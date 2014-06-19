# /opt/planetstack/core/dashboard/views/helloworld.py
import datetime
import os
import sys
import time
import json
from django.http import HttpResponse, HttpResponseServerError, HttpResponseForbidden
from django.views.generic import TemplateView, View
from core.models import *
from django.forms.models import model_to_dict

def ensure_serializable(d):
    d2={}
    for (k,v) in d.items():
        # datetime is not json serializable
        if isinstance(v, datetime.datetime):
            d2[k] = time.mktime(v.timetuple())
        else:
            d2[k] = v
    return d2

class ShellDataView(View):
    url = r'^shelldata/'

    def get(self, request, **kwargs):
        allSlices = []
        for slice in Slice.objects.all():
            allSlices.append(ensure_serializable(model_to_dict(slice)))

        result = {"slices": allSlices}

        return HttpResponse(json.dumps(result), mimetype='application/json')
