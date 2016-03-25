from django import template
import sys
from core.models import DashboardView
from itertools import chain

register = template.Library()

@register.inclusion_tag('admin/tags/dashboard_list.html', takes_context=True)
def dashboard_list(context):
    request = context['request']
    dashboards = request.user.get_dashboards()
    customize = DashboardView.objects.filter(name="Customize")
    # debug = DashboardView.objects.filter(name="Customize").values()
    print >>sys.stderr, request.user.get_dashboards()
    result_list = list(chain(dashboards, customize))
    return {'dashboards': result_list}