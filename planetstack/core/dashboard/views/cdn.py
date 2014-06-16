from view_common import *

class DashboardSummaryAjaxView(View):
    def get(self, request, **kwargs):
        def avg(x):
            if len(x)==0:
                return 0
            return float(sum(x))/len(x)

        sites = getCDNOperatorData().values()

        sites = [site for site in sites if site["numHPCSlivers"]>0]

        total_slivers = sum( [site["numHPCSlivers"] for site in sites] )
        total_bandwidth = sum( [site["bandwidth"] for site in sites] )
        average_cpu = int(avg( [site["load"] for site in sites] ))

        result= {"total_slivers": total_slivers,
                "total_bandwidth": total_bandwidth,
                "average_cpu": average_cpu}

        return HttpResponse(json.dumps(result), content_type='application/javascript')

class DashboardAddOrRemoveSliverView(View):
    # TODO: deprecate this view in favor of using TenantAddOrRemoveSliverView

    def post(self, request, *args, **kwargs):
        siteName = request.POST.get("site", None)
        actionToDo = request.POST.get("actionToDo", "0")

        siteList = [Site.objects.get(name=siteName)]
        slice = Slice.objects.get(name="HyperCache")

        if request.user.isReadOnlyUser():
            return HttpResponseForbidden("User is in read-only mode")

        if (actionToDo == "add"):
            user_ip = request.GET.get("ip", get_ip(request))
            slice_increase_slivers(request.user, user_ip, siteList, slice, 1)
        elif (actionToDo == "rem"):
            slice_decrease_slivers(request.user, siteList, slice, 1)

        print '*' * 50
        print 'Ask for site: ' + siteName + ' to ' + actionToDo + ' another HPC Sliver'
        return HttpResponse(json.dumps("Success"), content_type='application/javascript')

class DashboardAjaxView(View):
    def get(self, request, **kwargs):
        return HttpResponse(json.dumps(getCDNOperatorData(True)), content_type='application/javascript')
