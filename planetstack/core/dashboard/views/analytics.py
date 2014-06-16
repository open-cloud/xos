from view_common import *
import random

class DashboardAnalyticsAjaxView(View):
    def get(self, request, name="hello_world", **kwargs):
        if (name == "bigquery"):
            (mimetype, data) = DoPlanetStackAnalytics(request)
            return HttpResponse(data, content_type=mimetype)
        else:
            return HttpResponse(json.dumps("Unknown"), content_type='application/javascript')
