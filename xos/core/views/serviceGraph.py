from django.http import HttpResponse
from django.views.generic import TemplateView, View
from django import template
from core.models import *
from core.dashboard.views import DashboardDynamicView
from xos.config import XOS_DIR
import json
import os
import time
import tempfile


class ServiceGridView(TemplateView):

    head_template = r"""{% extends "admin/dashboard/dashboard_base.html" %}
       {% load admin_static %}
       {% block content %}
    """

    tail_template = r"{% endblock %}"

    def readTemplate(self, fn):
        TEMPLATE_DIRS = [XOS_DIR + "/templates/admin/dashboard/",
                         XOS_DIR + "/core/xoslib/dashboards/"]

        for template_dir in TEMPLATE_DIRS:
            pathname = os.path.join(template_dir, fn) + ".html"
            if os.path.exists(pathname):
                break
        else:
            return "failed to find %s in %s" % (fn, TEMPLATE_DIRS)

        template = open(pathname, "r").read()
        return template

    def get(self, request, name="root", *args, **kwargs):

        dash = DashboardView.objects.get(name="Services Grid")

        gridTemplate = self.readTemplate(dash.url[9:])

        t = template.Template(self.head_template + gridTemplate + self.tail_template)

        response_kwargs = {}
        response_kwargs.setdefault('content_type', self.content_type)

        return self.response_class(
            request=request,
            template=t,
            **response_kwargs)
