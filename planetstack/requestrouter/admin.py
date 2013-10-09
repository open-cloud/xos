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
from core.admin import SingletonAdmin,SliceInline,ServiceAttrAsTabInline

class RequestRouterServiceAdmin(SingletonAdmin):
    model = RequestRouterService
    verbose_name = "Request Router Service"
    verbose_name_plural = "Request Router Service"
    list_display = ("name","enabled")
    fieldsets = [(None, {'fields': ['name','enabled','versionNumber', 'description','behindNat','defaultTTL','defaultAction','lastResortAction','maxAnswers'], 'classes':['suit-tab suit-tab-general']})]
    inlines = [SliceInline,ServiceAttrAsTabInline]

    suit_form_tabs =(('general', 'Request Router Service Details'),
        ('slices','Slices'),
        ('serviceattrs','Additional Attributes'),
    )


admin.site.register(RequestRouterService, RequestRouterServiceAdmin)
admin.site.register(ClientMap)

