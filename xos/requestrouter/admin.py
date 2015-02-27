from django.contrib import admin

from requestrouter.models import *
from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone
from django.contrib.contenttypes import generic
from suit.widgets import LinkedSelect
from core.admin import ServiceAppAdmin,SliceInline,ServiceAttrAsTabInline, ReadOnlyAwareAdmin

class RequestRouterServiceAdmin(ServiceAppAdmin):
    model = RequestRouterService
    verbose_name = "Request Router Service"
    verbose_name_plural = "Request Router Service"
    list_display = ("name","enabled")
    fieldsets = [(None, {'fields': ['name','enabled','versionNumber', 'description','behindNat','defaultTTL','defaultAction','lastResortAction','maxAnswers'], 'classes':['suit-tab suit-tab-general']})]
    inlines = [SliceInline,ServiceAttrAsTabInline]

    user_readonly_fields = ["name", "enabled", "versionNumber", "description", "behindNat", "defaultTTL", "defaultAction", "lastResortAction", "maxAnswers"]

    suit_form_tabs =(('general', 'Request Router Service Details'),
        ('administration', 'Administration'),
        ('slices','Slices'),
        ('serviceattrs','Additional Attributes'),
    )

    suit_form_includes = (('rradmin.html', 'top', 'administration'),)

class ServiceMapAdmin(ReadOnlyAwareAdmin):
    model = ServiceMap
    verbose_name = "Service Map"
    verbose_name_plural = "Service Map"
    list_display = ("name", "owner", "slice", "prefix")
    fieldsets = [(None, {'fields': ['name','owner','slice', 'prefix','siteMap','accessMap'], 'classes':['suit-tab suit-tab-general']})]

    user_readonly_fields = ["name", "owner", "slice", "prefix", "siteMap", "accessMap"]

    suit_form_tabs =(('general', 'Service Map Details'),
    )

admin.site.register(RequestRouterService, RequestRouterServiceAdmin)
admin.site.register(ServiceMap, ServiceMapAdmin)

