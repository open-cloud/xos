from django import template
# import sys
from core.models import DashboardView
from itertools import chain
from core.dashboard.views.home import DashboardDynamicView

register = template.Library()


@register.inclusion_tag('admin/tags/dashboard_list.html', takes_context=True)
def dashboard_list(context):
    request = context['request']
    if request.user.is_authenticated():
        dashboards = request.user.get_dashboards()
        customize = DashboardView.objects.filter(name="Customize")
        dashboards_list = list(chain(dashboards, customize))
    else:
        dashboards_list = []

    active = None
    for d in dashboards_list:
        if str(d.id) in request.path and "admin/dashboard" in request.path:
            active = d.id

    if active is None and ("/admin/" == request.path or "/" == request.path):
        active = dashboards[0].id

    return {'dashboards': dashboards_list, 'active': active}


@register.inclusion_tag('admin/tags/notification.html', takes_context=True)
def notification(context):
    template = DashboardDynamicView.readTemplate(DashboardDynamicView(), "xosSynchronizerNotifier")
    return {'template': template}
