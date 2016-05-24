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


class ServiceGridViewPy(TemplateView):
    head_template = r"""{% extends "admin/dashboard/dashboard_base.html" %}
       {% load admin_static %}
       {% block content %}
    """

    tail_template = r"{% endblock %}"

    def get(self, request, name="root", *args, **kwargs):
        head_template = self.head_template
        tail_template = self.tail_template

        html = '<table class="service-grid"><tr>'

        icons = []
        for service in Service.objects.all():
            view_url = service.view_url
            if (not view_url):
                view_url = "/admin/core/service/$id$/"
            view_url = view_url.replace("$id$", str(service.id))

            image_url = service.icon_url
            if (not image_url):
                image_url = "/static/primarycons_blue/gear_2.png"

            icons.append({"name": service.name, "view_url": view_url, "image_url": image_url})

        icons.append({"name": "Tenancy Graph", "view_url": "/serviceGraph.png", "image_url": "/static/primarycons_blue/service_graph.png", "horiz_rule": True})
        icons.append({"name": "Add Service", "view_url": "/admin/core/service/add/", "image_url": "/static/primarycons_blue/plus.png"})

        i = 0
        for icon in icons:
            if icon.get("horiz_rule", False):
                html = html + "</tr><tr><td colspan=4><hr></td></tr><tr>"
                i = 0

            service_name = icon["name"]
            view_url = icon["view_url"]
            image_url = icon["image_url"]

            if (i % 4) == 0:
                html = html + '</tr><tr>'

            html = html + '<td width=96 height=128 valign=top align=center><a class="service-grid-icon" href="%s"><img src="%s" height=64 width=64></img></a>' % (view_url, image_url)
            html = html + '<p><a class="service-grid-icon-link" href="%s">%s</a></p></td>' % (view_url, service_name)
            i = i+1

        html = html + '</tr></table>'

        t = template.Template(head_template + html + self.tail_template)

        response_kwargs = {}
        response_kwargs.setdefault('content_type', self.content_type)
        return self.response_class(
            request=request,
            template=t,
            **response_kwargs
        )


class ServiceGraphViewOld(TemplateView):
    #  this attempt used networkx
    # yum -y install python-matplotlib python-networkx
    # pip-python install -upgrade networkx
    # pip-python install graphviz pygraphviz

    def get(self, request, name="root", *args, **kwargs):
        import networkx as nx
        import matplotlib as mpl
        mpl.use("Agg")
        import matplotlib.pyplot as plt
        import nxedges

        plt.figure(figsize=(10, 8))

        g = nx.DiGraph()

        labels = {}
        for service in Service.objects.all():
            g.add_node(service.id)
            if len(service.name) > 8:
                labels[service.id] = service.name[:8] + "\n" + service.name[8:]
            else:
                labels[service.id] = service.name

        for tenant in CoarseTenant.objects.all():
            if (not tenant.provider_service) or (not tenant.subscriber_service):
                continue
            g.add_edge(tenant.subscriber_service.id, tenant.provider_service.id)

        pos = nx.graphviz_layout(g)
        nxedges.xos_draw_networkx_edges(g, pos, arrow_len=30)
        nx.draw_networkx_nodes(g, pos, node_size=5000)
        nx.draw_networkx_labels(g, pos, labels, font_size=12)
        # plt.axis('off')
        plt.savefig("/tmp/foo.png")

        return HttpResponse(open("/tmp/foo.png", "r").read(), content_type="image/png")


class ServiceGraphView(TemplateView):
    # this attempt just uses graphviz directly
    # yum -y install graphviz
    # pip-python install pygraphviz

    def get(self, request, name="root", *args, **kwargs):
        import pygraphviz as pgv

        g = pgv.AGraph(directed=True)
        g.graph_attr.update(size="8,4!")
        g.graph_attr.update(dpi="100")
        # g.graph_attr.update(nodesep="2.5")
        g.graph_attr.update(overlap="false")
        g.graph_attr.update(graphdir="TB")

        for service in Service.objects.all():
            provided_tenants = Tenant.objects.filter(provider_service=service, subscriber_service__isnull=False)
            subscribed_tenants = Tenant.objects.filter(subscriber_service=service, provider_service__isnull=False)
            if not (provided_tenants or subscribed_tenants):
                # nodes with no edges aren't interesting
                continue
            g.add_node(service.id, label=service.name)

        for tenant in Tenant.objects.all():
            if (not tenant.provider_service) or (not tenant.subscriber_service):
                continue
            g.add_edge(tenant.subscriber_service.id, tenant.provider_service.id)

        tf = tempfile.TemporaryFile()
        g.layout(prog="dot")
        g.draw(path=tf, format="png")
        tf.seek(0)

        return HttpResponse(tf.read(), content_type="image/png")
