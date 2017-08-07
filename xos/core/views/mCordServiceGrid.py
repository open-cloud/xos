
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


from django.http import HttpResponse
from django.views.generic import TemplateView, View
from django import template
from django.shortcuts import render
from core.models import *
import json
import os
import time
import tempfile


class ServiceGridView(TemplateView):
    head_template = r"""{% extends "admin/dashboard/dashboard_base.html" %}
       {% load admin_static %}
       {% block content %}
    """

    # I hate myself for doing this
    script = """
    <script type="text/javascript">
        $(window).ready(function(){
            $('.kind-container').on('click', function(){
                $(this).toggleClass('active')
            });
        })
    </script>
    <style>
        .kind-container.row {
            height: 60px;
            overflow-y: hidden;
            transition: all .5s ease-in-out;
        }

        .kind-container.row > .col-xs-12 {
            margin-bottom:10px;
            background: darkred;
            color: #fff;
            border-radius: 10px;
        }

        .kind-container.row.active {
            height: 230px;
        }

        .kind-container img {
            margin: 0 auto;
        }
    </style>
    """

    tail_template = r"{% endblock %}"

    def get(self, request, name="root", *args, **kwargs):
        head_template = self.head_template
        tail_template = self.tail_template
        html = self.script
        html = html + '<div class="col-xs-12 m-cord">'

        # Select the unique kind of services
        for kind in Service.objects.values('kind').distinct():

            html = html + '<div class="kind-container row">'
            html = html + '<div class="col-xs-12"><h2>%s</h2></div>' % (kind["kind"])

            # for each kind select services
            for service in Service.objects.filter(kind=kind["kind"]):
                image_url = service.icon_url
                if (not image_url):
                    image_url = "/static/mCordServices/service_common.png"
                #if service.view_url.startswith("http"):
                #    target = 'target="_blank"'
                #else:
                #    target = ''
                target = ''

                html = html + '<div class="col-xs-4 text-center service-container">'
                html = html + '<a href="%s" %s>' % (service.view_url.replace("$id$", str(service.id)), target)
                html = html + '<img class="img-responsive" src="%s">' % (image_url)
                html = html + "<h4>" + service.name + "</h4>"
                html = html + '</a>'
                html = html + "</div>"

            html = html + "</div>"

        html = html + "</div>"
        t = template.Template(head_template + html + self.tail_template)

        response_kwargs = {}
        response_kwargs.setdefault('content_type', self.content_type)
        return self.response_class(
            request=request,
            template=t,
            **response_kwargs
        )
