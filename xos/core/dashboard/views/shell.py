
# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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

def instance_to_dict(instance):
    d = model_to_dict(instance)
    d["slice_id"] = instance.slice.id
    d["node_id"] = instance.node.id
    return d

def slice_to_dict(slice):
    d = model_to_dict(slice)
    d["instances"] = [instance_to_dict(x) for x in slice.instances]
    return d

def node_to_dict(node):
    d = model_to_dict(node)
    d["instances"] = []


class OpenCloudData:
    def __init__(self, user):
        self.loadAll()

    def loadAll(self):
        self.allNodes = list(Node.objects.all())
        self.allSlices = list(Slice.objects.all())
        self.allInstances = list(Instance.objects.all())
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
            d["instance_ids"] = []
            self.node_id[node.id] = ensure_serializable(d)
            self.site_id[node.site_id]["node_ids"].append(node.id)

        self.slice_id = {}
        for slice in self.allSlices:
            d = model_to_dict(slice)
            d["instance_ids"] = []
            self.slice_id[slice.id] = ensure_serializable(d)
            self.site_id[slice.site_id]["slice_ids"].append(site.id)

        print self.slice_id.keys()

        self.instance_id = {}
        for instance in self.allInstances:
            self.instance_id[instance.id] = model_to_dict(instance)

            self.slice_id[instance.slice_id]["instance_ids"].append(instance.id)
            self.node_id[instance.node_id]["instance_ids"].append(instance.id)

    def get_opencloud_data(self):
        return {"slices": self.slice_id.values(),
                "instances": self.instance_id.values(),
                "nodes": self.node_id.values(),
                "sites": self.site_id.values()}

class ShellDataView(View):
    url = r'^shelldata/'

    def get(self, request, **kwargs):
        result = OpenCloudData(request.user).get_opencloud_data()

        return HttpResponse(json.dumps(result), mimetype='application/json')
