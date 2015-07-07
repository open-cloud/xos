from django.contrib import admin

from cord.models import *
from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone
from django.contrib.contenttypes import generic
from suit.widgets import LinkedSelect
from core.admin import ServiceAppAdmin,SliceInline,ServiceAttrAsTabInline, ReadOnlyAwareAdmin, XOSTabularInline, ServicePrivilegeInline

from functools import update_wrapper
from django.contrib.admin.views.main import ChangeList
from django.core.urlresolvers import reverse
from django.contrib.admin.utils import quote

#-----------------------------------------------------------------------------
# vOLT
#-----------------------------------------------------------------------------

class VOLTServiceAdmin(ReadOnlyAwareAdmin):
    model = VOLTService
    verbose_name = "vOLT Service"
    verbose_name_plural = "vOLT Service"
    list_display = ("backend_status_icon", "name", "enabled")
    list_display_links = ('backend_status_icon', 'name', )
    fieldsets = [(None, {'fields': ['backend_status_text', 'name','enabled','versionNumber', 'description',"view_url","icon_url" ], 'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', )
    inlines = [SliceInline,ServiceAttrAsTabInline,ServicePrivilegeInline]

    extracontext_registered_admins = True

    user_readonly_fields = ["name", "enabled", "versionNumber", "description"]

    suit_form_tabs =(('general', 'vOLT Service Details'),
        ('administration', 'Administration'),
        #('tools', 'Tools'),
        ('slices','Slices'),
        ('serviceattrs','Additional Attributes'),
        ('serviceprivileges','Privileges'),
    )

    suit_form_includes = (('voltadmin.html', 'top', 'administration'),
                           ) #('hpctools.html', 'top', 'tools') )

    def queryset(self, request):
        return VOLTService.get_service_objects()

class VOLTTenantForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super (VOLTTenantForm,self ).__init__(*args,**kwargs)
        self.fields['kind'].default = "vOLT"
        self.fields['kind'].widget.attrs['readonly'] = True
        self.fields['provider_service'].queryset = VOLTService.get_service_objects().all()

    class Meta:
        model = VOLTTenant

class VOLTTenantAdmin(ReadOnlyAwareAdmin):
    list_display = ('backend_status_icon', 'id', 'service_specific_id', 'vlan_id', 'subscriber_root' )
    list_display_links = ('backend_status_icon', 'id')
    fieldsets = [ (None, {'fields': ['backend_status_text', 'kind', 'provider_service', 'subscriber_root', 'service_specific_id', 'service_specific_attribute',], 'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', )
    form = VOLTTenantForm

    suit_form_tabs = (('general','Details'),)

    def queryset(self, request):
        return VOLTTenant.get_tenant_objects()

#-----------------------------------------------------------------------------
# vCPE
#-----------------------------------------------------------------------------

class VCPEServiceAdmin(ReadOnlyAwareAdmin):
    model = VCPEService
    verbose_name = "vCPE Service"
    verbose_name_plural = "vCPE Service"
    list_display = ("backend_status_icon", "name", "enabled")
    list_display_links = ('backend_status_icon', 'name', )
    fieldsets = [(None, {'fields': ['backend_status_text', 'name','enabled','versionNumber', 'description', "view_url","icon_url" ], 'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', )
    inlines = [SliceInline,ServiceAttrAsTabInline,ServicePrivilegeInline]

    extracontext_registered_admins = True

    user_readonly_fields = ["name", "enabled", "versionNumber", "description"]

    suit_form_tabs =(('general', 'vCPE Service Details'),
        ('administration', 'Administration'),
        #('tools', 'Tools'),
        ('slices','Slices'),
        ('serviceattrs','Additional Attributes'),
        ('serviceprivileges','Privileges') ,
    )

    suit_form_includes = (('vcpeadmin.html', 'top', 'administration'),
                           ) #('hpctools.html', 'top', 'tools') )

    def queryset(self, request):
        return VCPEService.get_service_objects()

class VCPETenantForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super (VCPETenantForm,self ).__init__(*args,**kwargs)
        self.fields['kind'].default = "vCPE"
        self.fields['kind'].widget.attrs['readonly'] = True
        self.fields['provider_service'].queryset = VCPEService.get_service_objects().all()

    class Meta:
        model = VCPETenant

class VCPETenantAdmin(ReadOnlyAwareAdmin):
    list_display = ('backend_status_icon', 'id', 'subscriber_tenant' )
    list_display_links = ('backend_status_icon', 'id')
    fieldsets = [ (None, {'fields': ['backend_status_text', 'kind', 'provider_service', 'subscriber_tenant', 'service_specific_id', 'service_specific_attribute',], 'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', )
    form = VCPETenantForm

    suit_form_tabs = (('general','Details'),)

    def queryset(self, request):
        return VCPETenant.get_tenant_objects()

#-----------------------------------------------------------------------------
# vBNG
#-----------------------------------------------------------------------------

class VBNGServiceAdmin(ReadOnlyAwareAdmin):
    model = VBNGService
    verbose_name = "vBNG Service"
    verbose_name_plural = "vBNG Service"
    list_display = ("backend_status_icon", "name", "enabled")
    list_display_links = ('backend_status_icon', 'name', )
    fieldsets = [(None, {'fields': ['backend_status_text', 'name','enabled','versionNumber', 'description', "view_url","icon_url" ], 'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', )
    inlines = [SliceInline,ServiceAttrAsTabInline,ServicePrivilegeInline]

    extracontext_registered_admins = True

    user_readonly_fields = ["name", "enabled", "versionNumber", "description"]

    suit_form_tabs =(('general', 'vBNG Service Details'),
        ('administration', 'Administration'),
        #('tools', 'Tools'),
        ('slices','Slices'),
        ('serviceattrs','Additional Attributes'),
        ('serviceprivileges','Privileges'),
    )

    suit_form_includes = (('vbngadmin.html', 'top', 'administration'),
                           ) #('hpctools.html', 'top', 'tools') )

    def queryset(self, request):
        return VBNGService.get_service_objects()

class VBNGTenantForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super (VBNGTenantForm,self ).__init__(*args,**kwargs)
        self.fields['kind'].default = "vBNG"
        self.fields['kind'].widget.attrs['readonly'] = True
        self.fields['provider_service'].queryset = VBNGService.get_service_objects().all()

    class Meta:
        model = VBNGTenant

class VBNGTenantAdmin(ReadOnlyAwareAdmin):
    list_display = ('backend_status_icon', 'id', 'subscriber_tenant' )
    list_display_links = ('backend_status_icon', 'id')
    fieldsets = [ (None, {'fields': ['backend_status_text', 'kind', 'provider_service', 'subscriber_tenant', 'service_specific_id', 'service_specific_attribute',], 'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', )
    form = VBNGTenantForm

    suit_form_tabs = (('general','Details'),)

    def queryset(self, request):
        return VBNGTenant.get_tenant_objects()

admin.site.register(VOLTService, VOLTServiceAdmin)
admin.site.register(VOLTTenant, VOLTTenantAdmin)
admin.site.register(VCPEService, VCPEServiceAdmin)
admin.site.register(VCPETenant, VCPETenantAdmin)
admin.site.register(VBNGService, VBNGServiceAdmin)
admin.site.register(VBNGTenant, VBNGTenantAdmin)

