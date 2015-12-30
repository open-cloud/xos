from django.contrib import admin

from urlfilter.models import *
from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone
from django.contrib.contenttypes import generic
from suit.widgets import LinkedSelect
from core.admin import SingletonAdmin,SliceInline,ServiceAttrAsTabInline, ReadOnlyAwareAdmin, PlStackTabularInline

class UrlFilterServiceAdmin(SingletonAdmin):
    model = UrlFilterService
    verbose_name = "Url Filter Service"
    verbose_name_plural = "Url Filter Service"
    list_display = ("backend_status_icon", "name","enabled")
    list_display_links = ('backend_status_icon', 'name', )
    fieldsets = [(None, {'fields': ['backend_status_text', 'name','enabled','versionNumber', 'description'], 'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', )
    inlines = [SliceInline,ServiceAttrAsTabInline]

    user_readonly_fields = ["name", "enabled", "versionNumber", "description"]

    suit_form_tabs =(('general', 'URL Filter Details'),
        ('slices','Slices'),
        ('serviceattrs','Additional Attributes'),
    )

admin.site.register(UrlFilterService, UrlFilterServiceAdmin)

