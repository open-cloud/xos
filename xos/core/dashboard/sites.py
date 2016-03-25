#sites.py

from django.contrib.admin.sites import AdminSite


class AdminMixin(object):
    """Mixin for AdminSite to allow custom dashboard views."""

    def __init__(self, *args, **kwargs):
        return super(AdminMixin, self).__init__(*args, **kwargs)

    def get_urls(self):
        """Add our dashboard view to the admin urlconf. Deleted the default index."""
        from django.conf.urls import patterns, url
        from views import DashboardCustomize, DashboardDynamicView, SimulatorView, LoggedInView, \
                          DashboardUserSiteView,  \
                          TenantViewData, TenantCreateSlice, TenantAddUser,TenantAddOrRemoveInstanceView, TenantPickSitesView, TenantDeleteSliceView, \
                          TenantUpdateSlice, DashboardSliceInteractions, RequestAccessView

        from views import view_urls

        urls = super(AdminMixin, self).get_urls()
        del urls[0]

        # these ones are for the views that were written before we implemented
        # the ability to get the url from the View class.
        dashboard_urls = [
               url(r'^$', self.admin_view(DashboardDynamicView.as_view()),
                    name="index"),
               url(r'^loggedin/$', self.admin_view(LoggedInView.as_view()),
                    name="loggedin"),
               url(r'^test/', self.admin_view(DashboardUserSiteView.as_view()),
                    name="test"),
               url(r'^sliceinteractions/(?P<name>\w+)/$', self.admin_view(DashboardSliceInteractions.as_view()),
                    name="interactions"),
               url(r'^dashboard/(?P<name>[\w|\W]+)/$', self.admin_view(DashboardDynamicView.as_view()),
                    name="dashboard"),
               url(r'^dashboardWholePage/(?P<name>\w+)/$', self.admin_view(DashboardDynamicView.as_view()),
                    {"wholePage": True},
                    name="dashboardWholePage"),
	       url(r'^customize/$', self.admin_view(DashboardCustomize.as_view()),
                    name="customize"),
               url(r'^hpcdashuserslices/', self.admin_view(DashboardUserSiteView.as_view()),
                    name="hpcdashuserslices"),
               url(r'^welcome/$', self.admin_view(DashboardDynamicView.as_view()),
                    name="welcome"),
               url(r'^simulator/', self.admin_view(SimulatorView.as_view()),
                    name="simulator"),
               url(r'^tenantaddorreminstance/$', self.admin_view(TenantAddOrRemoveInstanceView.as_view()),
                    name="tenantaddorreminstance"),
               url(r'^tenantview/$', self.admin_view(TenantViewData.as_view()),
                    name="tenantview"),
               url(r'^createnewslice/$', self.admin_view(TenantCreateSlice.as_view()),
                    name="createnewslice"),
               url(r'^adduser/$', self.admin_view(TenantAddUser.as_view()),
                      name="adduser"),
               url(r'^requestaccess/$', RequestAccessView.as_view(),
                      name="requestacces"),
	       url(r'^updateslice/$', self.admin_view(TenantUpdateSlice.as_view()),
                    name="updateslice"),
               url(r'^picksites/$', self.admin_view(TenantPickSitesView.as_view()),
                    name="picksites"),
	       url(r'^tenantdeleteslice/$', self.admin_view(TenantDeleteSliceView.as_view()),
                    name="tenantdeleteslice")
        ]

        # these ones are for the views that have a "url" member in the class
        for (view_url, view_classname, view_class) in view_urls:
            dashboard_urls.append( url(view_url, self.admin_view(view_class.as_view()), name=view_classname.lower()))

        return dashboard_urls + urls


class SitePlus(AdminMixin, AdminSite):
    """
    A Django AdminSite with the AdminMixin to allow registering custom
    dashboard view.
    """
