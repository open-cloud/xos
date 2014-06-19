# /opt/planetstack/core/dashboard/views/helloworld.py
import os
import sys
import json
from django.http import HttpResponse, HttpResponseServerError, HttpResponseForbidden
from django.views.generic import TemplateView, View
from core.models import *
from django.forms.models import model_to_dict

class ShellDataView(View):
    url = r'^shelldata/'

    def get(self, request, **kwargs):
        allSlices = []
        for slice in Slice.objects.all():
            allSlices.append(model_to_dict(slice))

        result = {"slices": allSlices}

        return HttpResponse(json.dumps(result), mimetype='application/json')
