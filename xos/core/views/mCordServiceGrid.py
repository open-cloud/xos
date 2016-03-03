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
                html = html + '<a href="%s" %s>' % (service.view_url, target)
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
