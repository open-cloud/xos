from core.admin import (ReadOnlyAwareAdmin, ServiceAppAdmin,
                        ServiceAttrAsTabInline, ServicePrivilegeInline,
                        SliceInline)
from django.contrib import admin
from services.requestrouter.models import RequestRouterService, ServiceMap


class RequestRouterAdmin(ReadOnlyAwareAdmin):
    # Change the application breadcrumb to point to an RR Service if one is
    # defined

    change_form_template = "admin/change_form_bc.html"
    change_list_template = "admin/change_list_bc.html"
    custom_app_breadcrumb_name = "Request Router"

    @property
    def custom_app_breadcrumb_url(self):
        services = RequestRouterService.objects.all()
        if len(services) == 1:
            return "/admin/requestrouter/requestrouterservice/%s/" % services[0].id
        else:
            return "/admin/requestrouter/requestrouterservice/"


class RequestRouterServiceAdmin(ServiceAppAdmin):
    model = RequestRouterService
    verbose_name = "Request Router Service"
    verbose_name_plural = "Request Router Service"
    list_display = ("name", "enabled")
    fieldsets = [(None, {'fields': ['name', 'enabled', 'versionNumber', 'description', 'behindNat', 'defaultTTL',
                                    'defaultAction', 'lastResortAction', 'maxAnswers'], 'classes':['suit-tab suit-tab-general']})]
    inlines = [SliceInline, ServiceAttrAsTabInline, ServicePrivilegeInline]

    user_readonly_fields = ["name", "enabled", "versionNumber", "description",
                            "behindNat", "defaultTTL", "defaultAction", "lastResortAction", "maxAnswers"]

    suit_form_tabs = (('general', 'Request Router Service Details'),
                      ('administration', 'Administration'),
                      ('slices', 'Slices'),
                      ('serviceattrs', 'Additional Attributes'),
                      ('serviceprivileges', 'Privileges'),
                      )

    suit_form_includes = (('rradmin.html', 'top', 'administration'),)


class ServiceMapAdmin(RequestRouterAdmin):
    model = ServiceMap
    verbose_name = "Service Map"
    verbose_name_plural = "Service Map"
    list_display = ("name", "owner", "slice", "prefix")
    fieldsets = [(None, {'fields': ['name', 'owner', 'slice', 'prefix',
                                    'siteMap', 'accessMap'], 'classes':['suit-tab suit-tab-general']})]

    user_readonly_fields = ["name", "owner",
                            "slice", "prefix", "siteMap", "accessMap"]

    suit_form_tabs = (('general', 'Service Map Details'),
                      )

admin.site.register(RequestRouterService, RequestRouterServiceAdmin)
admin.site.register(ServiceMap, ServiceMapAdmin)
