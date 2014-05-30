from view_common import *

class DashboardAnalyticsAjaxView(View):
    def get(self, request, name="hello_world", **kwargs):
        if (name == "hpcSummary"):
            return HttpResponse(json.dumps(hpc_wizard.get_hpc_wizard().get_summary_for_view()), mimetype='application/javascript')
        elif (name == "hpcUserSite"):
            return HttpResponse(json.dumps(getDashboardContext(request.user, tableFormat=True)), mimetype='application/javascript')
        elif (name == "hpcMap"):
            return HttpResponse(json.dumps(getCDNOperatorData(True)), mimetype='application/javascript')
        elif (name == "bigquery"):
            (mimetype, data) = DoPlanetStackAnalytics(request)
            return HttpResponse(data, mimetype=mimetype)
        else:
            return HttpResponse(json.dumps("Unknown"), mimetype='application/javascript')
