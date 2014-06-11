from django.contrib import admin

from kairos.models import *
from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone
from django.contrib.contenttypes import generic
from suit.widgets import LinkedSelect
from core.admin import SingletonAdmin,SliceInline,ServiceAttrAsTabInline, SliceROInline,ServiceAttrAsTabROInline, ReadOnlyAwareAdmin

class KairosDBServiceAdmin(SingletonAdmin):
    model = KairosDBService
    verbose_name = "KairosDB Service"
    verbose_name_plural = "KairosDB Service"
    list_display = ("name","enabled")
    fieldsets = [(None, {'fields': ['name','enabled','versionNumber', 'description'], 'classes':['suit-tab suit-tab-general']})]
    inlines = [SliceInline,ServiceAttrAsTabInline]

    user_readonly_inlines = [SliceROInline, ServiceAttrAsTabROInline]
    suit_form_tabs =(('general', 'KairosDB Service Details'),
        ('slices','Slices'),
        ('serviceattrs','Additional Attributes'),
    )

admin.site.register(KairosDBService, KairosDBServiceAdmin)

