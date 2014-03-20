#views.py
import os
import sys
from django.views.generic import TemplateView, View
import datetime
from pprint import pprint
import json
from core.models import Slice,SliceRole,SlicePrivilege,Site,Reservation,Sliver
from django.http import HttpResponse
import traceback

if os.path.exists("/home/smbaker/projects/vicci/cdn/bigquery"):
    sys.path.append("/home/smbaker/projects/vicci/cdn/bigquery")
else:
    sys.path.append("/opt/planetstack/hpc_wizard")
import hpc_wizard
from planetstack_analytics import DoPlanetStackAnalytics

class DashboardWelcomeView(TemplateView):
    template_name = 'admin/dashboard/welcome.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        userDetails = getUserSliceInfo(request.user)
        #context['site'] = userDetails['site']

        context['userSliceInfo'] = userDetails['userSliceInfo']
        context['cdnData'] = userDetails['cdnData']
        return self.render_to_response(context=context)

def getUserSliceInfo(user, tableFormat = False):
        userDetails = {}
#        try:
# //           site = Site.objects.filter(id=user.site.id)
#  //      except:
#   //         site = Site.objects.filter(name="Princeton")
#    //    userDetails['sitename'] = site[0].name
#     //   userDetails['siteid'] = site[0].id

        userSliceData = getSliceInfo(user)
        if (tableFormat):
#            pprint("*******      GET USER SLICE INFO")
            userDetails['userSliceInfo'] = userSliceTableFormatter(userSliceData)
        else:
            userDetails['userSliceInfo'] = userSliceData
        userDetails['cdnData'] = getCDNOperatorData();
#        pprint( userDetails)
        return userDetails

def userSliceTableFormatter(data):
#    pprint(data)
    formattedData = {
                     'rows' : data
                    }
    return formattedData

def getSliceInfo(user):
    sliceList = Slice.objects.all()
    slicePrivs = SlicePrivilege.objects.filter(user=user)
    userSliceInfo = []
    for entry in slicePrivs:

        slicename = Slice.objects.get(id=entry.slice.id).name
        sliceid = Slice.objects.get(id=entry.slice.id).id
        try:
            sliverList = Sliver.objects.filter(slice=entry.slice.id)
            siteList = {}
            for x in sliverList:
               if x.node.site not in siteList:
                  siteList[x.node.site] = 1
            slivercount = len(sliverList)
            sitecount = len(siteList)
        except:
            traceback.print_exc()
            slivercount = 0
            sitecount = 0

        userSliceInfo.append({'slicename': slicename, 'sliceid':sliceid,
                           'role': SliceRole.objects.get(id=entry.role.id).role, 'slivercount': slivercount, 'sitecount':sitecount})

    return userSliceInfo

def getCDNOperatorData(randomizeData = False):
    return hpc_wizard.get_hpc_wizard().get_sites_for_view()

def getPageSummary(request):
    slice = request.GET.get('slice', None)
    site = request.GET.get('site', None)
    node = request.GET.get('node', None)


class SimulatorView(View):
    def get(self, request, **kwargs):
        sim = json.loads(file("/tmp/simulator.json","r").read())
        text = "<html><head></head><body>"
        text += "Iteration: %d<br>" % sim["iteration"]
        text += "Elapsed since report %d<br><br>" % sim["elapsed_since_report"]
        text += "<table border=1>"
        text += "<tr><th>site</th><th>trend</th><th>weight</th><th>bytes_sent</th><th>hot</th></tr>"
        for site in sim["site_load"].values():
            text += "<tr>"
            text += "<td>%s</td><td>%0.2f</td><td>%0.2f</td><td>%d</td><td>%0.2f</td>" % \
                        (site["name"], site["trend"], site["weight"], site["bytes_sent"], site["load_frac"])
            text += "</tr>"
        text += "</table>"
        text += "</body></html>"
        return HttpResponse(text)

class DashboardUserSiteView(View):
    def get(self, request, **kwargs):
        return HttpResponse(json.dumps(getUserSliceInfo(request.user, True)), mimetype='application/javascript')

class DashboardSummaryAjaxView(View):
    def get(self, request, **kwargs):
        return HttpResponse(json.dumps(hpc_wizard.get_hpc_wizard().get_summary_for_view()), mimetype='application/javascript')

class DashboardAddOrRemoveSliverView(View):
    def post(self, request, *args, **kwargs):
        siteName = request.POST.get("site", "0")
        actionToDo = request.POST.get("actionToDo", "0")

        if (actionToDo == "add"):
            hpc_wizard.get_hpc_wizard().increase_slivers(siteName, 1)
        elif (actionToDo == "rem"):
            hpc_wizard.get_hpc_wizard().decrease_slivers(siteName, 1)

        print '*' * 50
        print 'Ask for site: ' + siteName + ' to ' + actionToDo + ' another HPC Sliver'
        return HttpResponse('This is POST request ')

class DashboardAjaxView(View):
    def get(self, request, **kwargs):
        return HttpResponse(json.dumps(getCDNOperatorData(True)), mimetype='application/javascript')

class DashboardAnalyticsAjaxView(View):
    def get(self, request, name="hello_world", **kwargs):
        if (name == "hpcSummary"):
            return HttpResponse(json.dumps(hpc_wizard.get_hpc_wizard().get_summary_for_view()), mimetype='application/javascript')
        elif (name == "hpcUserSite"):
            return HttpResponse(json.dumps(getUserSliceInfo(request.user, True)), mimetype='application/javascript')
        elif (name == "hpcMap"):
            return HttpResponse(json.dumps(getCDNOperatorData(True)), mimetype='application/javascript')
        elif (name == "bigquery"):
            (mimetype, data) = DoPlanetStackAnalytics(request)
            return HttpResponse(data, mimetype=mimetype)
        else:
            return HttpResponse(json.dumps("Unknown"), mimetype='application/javascript')

