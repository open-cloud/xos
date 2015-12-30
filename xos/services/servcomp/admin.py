from django.contrib import admin

from servcomp.models import *
from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone
from django.contrib.contenttypes import generic
from suit.widgets import LinkedSelect
from core.admin import SingletonAdmin,SliceInline,ServiceAttrAsTabInline, ReadOnlyAwareAdmin, XOSTabularInline

class ServiceInline(XOSTabularInline):
    model = CompositionServiceThrough
    verbose_name = "Service"
    verbose_name_plural = "Services"
    extra = 0
    #suit_classes = 'suit-tab suit-tab-general'
    fields = ('backend_status_icon', 'service', 'order')
    readonly_fields = ('backend_status_icon',)

class CompositionServiceAdmin(SingletonAdmin):
    model = CompositionService
    verbose_name = "Composition Service"
    verbose_name_plural = "Composition Service"
    list_display = ("backend_status_icon", "name","enabled")
    list_display_links = ('backend_status_icon', 'name', )
    fieldsets = [(None, {'fields': ['backend_status_text', 'name','enabled','versionNumber', 'description'], 'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', )
    inlines = [SliceInline,ServiceAttrAsTabInline]

    user_readonly_fields = ["name", "enabled", "versionNumber", "description"]

    suit_form_tabs =(('general', 'Composition Service Details'),
        ('slices','Slices'),
        ('serviceattrs','Additional Attributes'),
    )

class CompositionForm(forms.ModelForm):
    model = Composition
    class Media:
       js = ('/static/js/menu-sort-2.js',)

class CompositionAdmin(ReadOnlyAwareAdmin):
    list_display = ('backend_status_icon', 'name' )
    list_display_links = ('backend_status_icon', 'name' )
    form = CompositionForm

    fields = ('backend_status_text', 'name')
    readonly_fields = ('backend_status_text', )
    user_readonly_fields = ('name',)

    inlines = [ServiceInline]

class EndUserAdmin(ReadOnlyAwareAdmin):
    list_display = ('backend_status_icon', 'email', 'macAddress', 'composition' )
    list_display_links = ('backend_status_icon', 'email' )

    fields = ('backend_status_text', 'email', 'firstName', 'lastName', 'macAddress', 'composition')
    readonly_fields = ('backend_status_text', )
    user_readonly_fields = ('email', 'firstName', 'lastName', 'macAddress')

admin.site.register(CompositionService, CompositionServiceAdmin)
admin.site.register(Composition, CompositionAdmin)
admin.site.register(EndUser, EndUserAdmin)

