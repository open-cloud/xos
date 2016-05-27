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
        result_list = list(chain(dashboards, customize))
    else:
        result_list = []
    return {'dashboards': result_list, 'path': request.path}


@register.inclusion_tag('admin/tags/notification.html', takes_context=True)
def notification(context):
    template = DashboardDynamicView.readTemplate(DashboardDynamicView(), "xosSynchronizerNotifier")
    return {'template': template}
