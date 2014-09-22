from django.contrib import admin

from hpc.models import *
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

class RRServiceAdmin(SingletonAdmin):
    model = RRService
    verbose_name = "RR Service"
    verbose_name_plural = "RR Service"
    list_display = ("backend_status_icon", "name","enabled")
    list_display_links = ('backend_status_icon', 'name', )
    fieldsets = [(None, {'fields': ['backend_status_text', 'name','enabled','versionNumber', 'description'], 'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', )
    inlines = [SliceInline,ServiceAttrAsTabInline]

    user_readonly_fields = ["name", "enabled", "versionNumber", "description"]

    suit_form_tabs =(('general', 'RR Service Details'),
        ('slices','Slices'),
        ('serviceattrs','Additional Attributes'),
    )

class DNSNameInline(PlStackTabularInline):
    model = CDNPrefix
    extra = 0
    suit_classes = 'suit-tab suit-tab-prefixes'
    fields = ('dns_name_id', 'name', 'enabled')
    readonly_fields = ('dns_name_id',)

class DNSNameForm(forms.ModelForm):
    class Meta:
        widgets = {
            'contentProvider' : LinkedSelect
        }

class DNSNameAdmin(ReadOnlyAwareAdmin):
    form = CDNPrefixForm
    list_display = ['name']
    list_display_links = ('name', )
    fields = ['name', 'dns_name_id', 'description', 'enabled']
    readonly_fields = ( )
    user_readonly_fields = ['name', "dns_name_id", "description", "enabled"]


admin.site.register(DNSName, DNSNameAdmin)
admin.site.register(RRService, RRServiceAdmin)
