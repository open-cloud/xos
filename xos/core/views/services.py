from django.http import HttpResponse
from django.views.generic import TemplateView, View
from django import template
from monitor import driver
from core.models import *
import json
import os
import time

class ServiceGridView(TemplateView):
    head_template = r"""{% extends "admin/dashboard/dashboard_base.html" %}
       {% load admin_static %}
       {% block content %}
    """

    tail_template = r"{% endblock %}"

    def get(self, request, name="root", *args, **kwargs):
        head_template = self.head_template
        tail_template = self.tail_template

        html = '<table><tr>'

        i=0
        for service in Service.objects.all():
            if (i%4) == 0:
                html = html + '</tr><tr>'

            view_url = service.view_url
            if (not view_url):
                view_url = "/admin/core/service/$id$/"
            view_url = view_url.replace("$id$", str(service.id))

            image_url = service.icon_url
            if (not image_url):
                image_url = "/static/primarycons_blue/gear_2.png"

            html = html + '<td width=96 height=128 valign=top align=center><a href="%s"><img src="%s" height=64 width=64></img></a>' % (view_url, image_url)
            html = html + '<p><a href="%s">%s</a></p></td>' % (view_url, service.name)
            i=i+1

        html = html + '</tr></table>'

        t = template.Template(head_template + html + self.tail_template)

        response_kwargs = {}
        response_kwargs.setdefault('content_type', self.content_type)
        return self.response_class(
            request = request,
            template = t,
            **response_kwargs)


