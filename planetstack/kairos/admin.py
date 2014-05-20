from django.contrib import admin

from nagios.models import *
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

class NagiosServiceAdmin(SingletonAdmin):
    model = NagiosService
    verbose_name = "Nagios Service"
    verbose_name_plural = "Nagios Service"
    list_display = ("name","enabled")
    fieldsets = [(None, {'fields': ['name','enabled','versionNumber', 'description'], 'classes':['suit-tab suit-tab-general']})]
    inlines = [SliceInline,ServiceAttrAsTabInline]

    user_readonly_inlines = [SliceROInline, ServiceAttrAsTabROInline]
    suit_form_tabs =(('general', 'Nagios Service Details'),
        ('slices','Slices'),
        ('serviceattrs','Additional Attributes'),
    )

admin.site.register(NagiosService, NagiosServiceAdmin)

