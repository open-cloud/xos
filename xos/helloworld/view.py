from django.http import HttpResponse
from django.views.generic import TemplateView, View
from django import template
from monitor import driver
from core.models import *
from helloworld.models import *
import json
import os
import time
import tempfile

class HelloWorldView(TemplateView):
    head_template = r"""{% extends "admin/dashboard/dashboard_base.html" %}
       {% load admin_static %}
       {% block content %}
    """

    tail_template = r"{% endblock %}"

    def get(self, request, name="root", *args, **kwargs):
        head_template = self.head_template
        tail_template = self.tail_template

        try:
            hello_name = request.GET['hello_name']
            world_name = request.GET['world_name']
            instance_id_str = request.GET['instance_id']
            instance_id = int(instance_id_str)

            i = Instance.objects.get(pk=instance_id)
            i.pk=None
            i.userData=None
            i.instance_id=None
            i.instance_name=None
            i.enacted=None
            i.save()
            h = Hello(name=hello_name,instance_backref=i)
            h.save()
            w.save()

            t = template.Template(head_template + 'Done. New instance id: %r'%i.pk + self.tail_template)
        except KeyError:
            html = """<form>
                Hello string: <input type="text" name="hello_name" placeholder="Planet"><br>
                World string: <input type="text" name="world_name" placeholder="Earth"><br>
                Id of instance to copy: <input type="text" name="instance_id" placeholder="3"><br>
                <input type="submit" value="Submit">
                  </form>"""

            t = template.Template(head_template + html + self.tail_template)

        response_kwargs = {}
        response_kwargs.setdefault('content_type', self.content_type)
        return self.response_class(
            request = request,
            template = t,
            **response_kwargs)
