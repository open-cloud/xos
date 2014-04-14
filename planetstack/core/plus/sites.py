#sites.py

from django.contrib.admin.sites import AdminSite


class AdminMixin(object):
    """Mixin for AdminSite to allow custom dashboard views."""

    def __init__(self, *args, **kwargs):
        return super(AdminMixin, self).__init__(*args, **kwargs)

    def get_urls(self):
        """Add our dashboard view to the admin urlconf. Deleted the default index."""
        from django.conf.urls import patterns, url
        from views import DashboardWelcomeView, DashboardAjaxView, SimulatorView, DashboardSummaryAjaxView, DashboardAddOrRemoveSliverView, DashboardUserSiteView, DashboardAnalyticsAjaxView, TenantViewData,TenantCreateSlice, TenantAddOrRemoveSliverView, TenantPickSitesView

        urls = super(AdminMixin, self).get_urls()
        del urls[0]
        custom_url = patterns('',
               url(r'^$', self.admin_view(DashboardWelcomeView.as_view()),
                    name="index"),
               url(r'^test/', self.admin_view(DashboardUserSiteView.as_view()),
                    name="test"),
               url(r'^hpcdashuserslices/', self.admin_view(DashboardUserSiteView.as_view()),
                    name="hpcdashuserslices"),
               url(r'^hpcdashboard/', self.admin_view(DashboardAjaxView.as_view()),        # DEPRECATED
                    name="hpcdashboard"),
               url(r'^simulator/', self.admin_view(SimulatorView.as_view()),
                    name="simulator"),
               url(r'^hpcsummary/', self.admin_view(DashboardSummaryAjaxView.as_view()),   # DEPRECATED
                    name="hpcsummary"),
               url(r'^analytics/(?P<name>\w+)/$', DashboardAnalyticsAjaxView.as_view(),
                    name="analytics"),
               url(r'^dashboardaddorremsliver/$', self.admin_view(DashboardAddOrRemoveSliverView.as_view()),
                    name="addorremsliver"),
               url(r'^tenantaddorremsliver/$', self.admin_view(TenantAddOrRemoveSliverView.as_view()),
                    name="tenantaddorremsliver"),
               url(r'^tenantview/$', self.admin_view(TenantViewData.as_view()),
                    name="tenantview"),
               url(r'^createnewslice/$', self.admin_view(TenantCreateSlice.as_view()),
                    name="createnewslice"),
               url(r'^picksites/$', self.admin_view(TenantPickSitesView.as_view()),
                    name="picksites")
        )

        return custom_url + urls


class SitePlus(AdminMixin, AdminSite):
    """
    A Django AdminSite with the AdminMixin to allow registering custom
    dashboard view.
    """
