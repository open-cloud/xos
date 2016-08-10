from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework.exceptions import APIException
from xos.apibase import XOSListCreateAPIView, XOSRetrieveUpdateDestroyAPIView, XOSPermissionDenied
import json
from core.models import UserDashboardView, DashboardView
from api.xosapi_helpers import XOSViewSet, PlusModelSerializer


class DashboardsSerializer(PlusModelSerializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    url = serializers.CharField(read_only=True)
    shown = serializers.CharField(read_only=True)
    icon = serializers.CharField(read_only=True)

    class Meta:
        model = DashboardView
        fields = ('id', 'name', 'url', 'shown', 'icon')


class DashboardsList(XOSViewSet):
    method_kind = "viewset"
    method_name = "dashboards"
    base_name = "dashboards"

    queryset = DashboardView.objects.all()
    serializer_class = DashboardsSerializer

    @classmethod
    def get_urlpatterns(self, api_path="^"):
        patterns = []

        patterns.append(self.list_url("$", {"get": "get_dashboards", "post": "set_dashboards"}, "get_user_dashboards"))
        # patterns.append(self.list_url("(?P<pk>[a-zA-Z0-9\-_]+)/$", {"post": "set_dashboards"}, "set_user_dashboards"))

        return patterns

    def get_dashboards(self, request):
        if (not request.user.is_authenticated()):
            raise XOSPermissionDenied("You must be authenticated in order to use this API")
        else:
            user_id = request.user.id
            available_dashboards = DashboardView.objects.filter(enabled=True).exclude(name="Customize")
            user_dashboards = UserDashboardView.objects.filter(user_id=user_id)

            user_dashboards_ids = []
            user_dashboards_order = {}
            for d in user_dashboards:
                user_dashboards_ids.append(d.dashboardView.id)
                user_dashboards_order[d.dashboardView.id] = d.order

            list = []

            for d in available_dashboards:
                dash = {}
                if(d.id in user_dashboards_ids):
                    dash['shown'] = True
                    dash['order'] = user_dashboards_order[d.id]
                else:
                    dash['shown'] = False
                dash['name'] = d.name
                dash['url'] = d.url
                dash['id'] = d.id
                dash['icon'] = d.icon
                list.append(dash)

            return Response(list)

    def add_dashboard_to_user(self, user_id, dashboard_id, order):
        try:
            existing = UserDashboardView.objects.get(user_id=user_id, dashboardView_id=dashboard_id)
        except:
            # if the dashboard does not exist create a new entry
            new_dashboard = UserDashboardView()
            new_dashboard.user_id = user_id
            new_dashboard.dashboardView_id = dashboard_id
            new_dashboard.order = order
            new_dashboard.save()
            return new_dashboard

        # else update this one, and update order for the others
        if(existing.order is not order):
            # update all changed models
            updateList = UserDashboardView.objects.filter(user_id=user_id).filter(order__lt=existing.order).filter(order__gte=order).exclude(id=existing.id)

            for d in updateList:
                d.order = d.order + 1
                d.save()

            # update current model
            existing.order = order
            existing.save()
        return existing

    def remove_dashboard_from_user(self, user_id, dashboard_id):
        print user_id
        print dashboard_id
        dashboard = UserDashboardView.objects.get(user_id=user_id, dashboardView_id=dashboard_id)
        dashboard.delete(purge=True)

    def set_dashboards(self, request):
        dashboard_id = request.data.get("id", None)
        old_dashboard = request.data
        if (not request.user.is_authenticated()):
            raise XOSPermissionDenied("You must be authenticated in order to use this API")
        elif(not dashboard_id):
            raise XOSPermissionDenied("You should provide the dashboard ID")
        else:
            if(old_dashboard['shown'] is True):
                self.add_dashboard_to_user(request.user.id, dashboard_id, old_dashboard['order'])
            else:
                self.remove_dashboard_from_user(request.user.id, dashboard_id)
            return Response(old_dashboard)
