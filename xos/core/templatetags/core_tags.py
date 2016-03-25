from django import template
import sys
from core.models import DashboardView

register = template.Library()

print >>sys.stderr, 'Got loaded!'
@register.inclusion_tag('admin/tags/dashboard_list.html')
def dashboard_list():
    dashboards = DashboardView.objects.all()
    print >>sys.stderr, 'Requesting template!'
    print >>sys.stderr, dashboards
    return {'dashboards': dashboards}