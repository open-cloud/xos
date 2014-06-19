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
        elif v.__class__.__name__ == "Geoposition":
            pass
        else:
            d2[k] = v
    return d2

def sliver_to_dict(sliver):
    d = model_to_dict(sliver)
    d["slice_id"] = sliver.slice.id
    d["node_id"] = sliver.node.id
    return d

def slice_to_dict(slice):
    d = model_to_dict(slice)
    d["slivers"] = [sliver_to_dict(x) for x in slice.slivers]
    return d

def node_to_dict(node):
    d = model_to_dict(node)
    d["slivers"] = []


class OpenCloudData:
    def __init__(self, user):
        self.loadAll()

    def loadAll(self):
        self.allNodes = list(Node.objects.all())
        self.allSlices = list(Slice.objects.all())
        self.allSlivers = list(Sliver.objects.all())
        self.allSites = list(Site.objects.all())

        self.site_id = {}
        for site in self.allSites:
            d = model_to_dict(site)
            d["node_ids"] = []
            d["slice_ids"] = []
            self.site_id[site.id] = ensure_serializable(d)

        self.node_id = {}
        for node in self.allNodes:
            d = model_to_dict(node)
            d["sliver_ids"] = []
            self.node_id[node.id] = ensure_serializable(d)
            self.site_id[node.site_id]["node_ids"].append(node.id)

        self.slice_id = {}
        for slice in self.allSlices:
            d = model_to_dict(slice)
            d["sliver_ids"] = []
            self.slice_id[slice.id] = ensure_serializable(d)
            self.site_id[slice.site_id]["slice_ids"].append(site.id)

        print self.slice_id.keys()

        self.sliver_id = {}
        for sliver in self.allSlivers:
            self.sliver_id[sliver.id] = model_to_dict(sliver)

            self.slice_id[sliver.slice_id]["sliver_ids"].append(sliver.id)
            self.node_id[sliver.node_id]["sliver_ids"].append(sliver.id)

    def get_opencloud_data(self):
        return {"slices": self.slice_id.values(),
                "slivers": self.sliver_id.values(),
                "nodes": self.node_id.values(),
                "sites": self.site_id.values()}

class ShellDataView(View):
    url = r'^shelldata/'

    def get(self, request, **kwargs):
        result = OpenCloudData(request.user).get_opencloud_data()

        return HttpResponse(json.dumps(result), mimetype='application/json')
