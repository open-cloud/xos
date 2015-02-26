from view_common import *

class DashboardCustomize(View):
    def post(self, request, *args, **kwargs):
        if request.user.isReadOnlyUser():
            return HttpResponseForbidden("User is in read-only mode")

        dashboards = request.POST.get("dashboards", None)
        if not dashboards:
            dashboards=[]
        else:
            dashboards = [x.strip() for x in dashboards.split(",")]
            dashboards = [DashboardView.objects.get(name=x) for x in dashboards]

        request.user.userdashboardviews.all().delete()

        for i,dashboard in enumerate(dashboards):
            udbv = UserDashboardView(user=request.user, dashboardView=dashboard, order=i)
            udbv.save()

        return HttpResponse(json.dumps("Success"), content_type='application/javascript')

