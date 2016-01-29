from django.contrib import admin

from services.ceilometer.models import *
from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone
from django.contrib.contenttypes import generic
from suit.widgets import LinkedSelect
from core.admin import ServiceAppAdmin,SliceInline,ServiceAttrAsTabInline, ReadOnlyAwareAdmin, XOSTabularInline, ServicePrivilegeInline, TenantRootTenantInline, TenantRootPrivilegeInline, TenantAttrAsTabInline
from core.middleware import get_request

from functools import update_wrapper
from django.contrib.admin.views.main import ChangeList
from django.core.urlresolvers import reverse
from django.contrib.admin.utils import quote

class CeilometerServiceAdmin(ReadOnlyAwareAdmin):
    model = CeilometerService
    verbose_name = "Ceilometer Service"
    verbose_name_plural = "Ceilometer Service"
    list_display = ("backend_status_icon", "name", "enabled")
    list_display_links = ('backend_status_icon', 'name', )
    fieldsets = [(None, {'fields': ['backend_status_text', 'name','enabled','versionNumber', 'description',"view_url","icon_url" ], 'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', )
    inlines = [SliceInline,ServiceAttrAsTabInline,ServicePrivilegeInline]

    extracontext_registered_admins = True

    user_readonly_fields = ["name", "enabled", "versionNumber", "description"]

    suit_form_tabs =(('general', 'Ceilometer Service Details'),
        ('administration', 'Administration'),
        ('slices','Slices'),
        ('serviceattrs','Additional Attributes'),
        ('serviceprivileges','Privileges'),
    )

    suit_form_includes = (('ceilometeradmin.html', 'top', 'administration'),
                           )

    def queryset(self, request):
        return CeilometerService.get_service_objects_by_user(request.user)

class MonitoringChannelForm(forms.ModelForm):
    creator = forms.ModelChoiceField(queryset=User.objects.all())

    def __init__(self,*args,**kwargs):
        super (MonitoringChannelForm,self ).__init__(*args,**kwargs)
        self.fields['kind'].widget.attrs['readonly'] = True
        self.fields['provider_service'].queryset = CeilometerService.get_service_objects().all()
        if self.instance:
            # fields for the attributes
            self.fields['creator'].initial = self.instance.creator
        if (not self.instance) or (not self.instance.pk):
            # default fields for an 'add' form
            self.fields['kind'].initial = CEILOMETER_KIND
            self.fields['creator'].initial = get_request().user
            if CeilometerService.get_service_objects().exists():
               self.fields["provider_service"].initial = CeilometerService.get_service_objects().all()[0]


    def save(self, commit=True):
        self.instance.creator = self.cleaned_data.get("creator")
        return super(MonitoringChannelForm, self).save(commit=commit)

    class Meta:
        model = MonitoringChannel

class MonitoringChannelAdmin(ReadOnlyAwareAdmin):
    list_display = ('backend_status_icon', 'id', )
    list_display_links = ('backend_status_icon', 'id')
    fieldsets = [ (None, {'fields': ['backend_status_text', 'kind', 'provider_service', 'service_specific_attribute',
                                     'ceilometer_url', 'tenant_list_str',
                                     'instance', 'creator'],
                          'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', 'instance', 'service_specific_attribute', 'ceilometer_url', 'tenant_list_str')
    form = MonitoringChannelForm

    suit_form_tabs = (('general','Details'),)
    actions=['delete_selected_objects']

    def get_actions(self, request):
        actions = super(MonitoringChannelAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def delete_selected_objects(self, request, queryset):
        for obj in queryset:
            obj.delete()
    delete_selected_objects.short_description = "Delete Selected MonitoringChannel Objects"

    def queryset(self, request):
        return MonitoringChannel.get_tenant_objects_by_user(request.user)

class SFlowServiceForm(forms.ModelForm):
    sflow_port = forms.IntegerField(required=False)
    sflow_api_port = forms.IntegerField(required=False)

    def __init__(self,*args,**kwargs):
        super (SFlowServiceForm,self ).__init__(*args,**kwargs)
        if self.instance:
            # fields for the attributes
            self.fields['sflow_port'].initial = self.instance.sflow_port
            self.fields['sflow_api_port'].initial = self.instance.sflow_api_port
        if (not self.instance) or (not self.instance.pk):
            # default fields for an 'add' form
            self.fields['sflow_port'].initial = SFLOW_PORT
            self.fields['sflow_api_port'].initial = SFLOW_API_PORT

    def save(self, commit=True):
        self.instance.sflow_port = self.cleaned_data.get("sflow_port")
        self.instance.sflow_api_port = self.cleaned_data.get("sflow_api_port")
        return super(SFlowServiceForm, self).save(commit=commit)

    class Meta:
        model = SFlowService

class SFlowServiceAdmin(ReadOnlyAwareAdmin):
    model = SFlowService
    verbose_name = "SFlow Service"
    verbose_name_plural = "SFlow Service"
    list_display = ("backend_status_icon", "name", "enabled")
    list_display_links = ('backend_status_icon', 'name', )
    fieldsets = [(None, {'fields': ['backend_status_text', 'name','enabled','versionNumber', 'description',"view_url","sflow_port","sflow_api_port","icon_url" ], 'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', )
    inlines = [SliceInline,ServiceAttrAsTabInline,ServicePrivilegeInline]
    form = SFlowServiceForm

    extracontext_registered_admins = True

    user_readonly_fields = ["name", "enabled", "versionNumber", "description"]

    suit_form_tabs =(('general', 'SFlow Service Details'),
        ('administration', 'Administration'),
        ('slices','Slices'),
        ('serviceattrs','Additional Attributes'),
        ('serviceprivileges','Privileges'),
    )

    suit_form_includes = (('sflowadmin.html', 'top', 'administration'),
                           )

    def queryset(self, request):
        return SFlowService.get_service_objects_by_user(request.user)

class SFlowTenantForm(forms.ModelForm):
    creator = forms.ModelChoiceField(queryset=User.objects.all())
    listening_endpoint = forms.CharField(max_length=1024, help_text="sFlow listening endpoint in udp://IP:port format")

    def __init__(self,*args,**kwargs):
        super (SFlowTenantForm,self ).__init__(*args,**kwargs)
        self.fields['kind'].widget.attrs['readonly'] = True
        self.fields['provider_service'].queryset = SFlowService.get_service_objects().all()
        if self.instance:
            # fields for the attributes
            self.fields['creator'].initial = self.instance.creator
            self.fields['listening_endpoint'].initial = self.instance.listening_endpoint
        if (not self.instance) or (not self.instance.pk):
            # default fields for an 'add' form
            self.fields['kind'].initial = SFLOW_KIND
            self.fields['creator'].initial = get_request().user
            if SFlowService.get_service_objects().exists():
               self.fields["provider_service"].initial = SFlowService.get_service_objects().all()[0]

    def save(self, commit=True):
        self.instance.creator = self.cleaned_data.get("creator")
        self.instance.listening_endpoint = self.cleaned_data.get("listening_endpoint")
        return super(SFlowTenantForm, self).save(commit=commit)

    class Meta:
        model = SFlowTenant

class SFlowTenantAdmin(ReadOnlyAwareAdmin):
    list_display = ('backend_status_icon', 'creator', 'listening_endpoint' )
    list_display_links = ('backend_status_icon', 'listening_endpoint')
    fieldsets = [ (None, {'fields': ['backend_status_text', 'kind', 'provider_service', 'subscriber_service', 'service_specific_attribute', 'listening_endpoint',
                                     'creator'],
                          'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', 'instance', 'service_specific_attribute')
    inlines = [TenantAttrAsTabInline]
    form = SFlowTenantForm

    suit_form_tabs = (('general','Details'), ('tenantattrs', 'Attributes'))

    def queryset(self, request):
        return SFlowTenant.get_tenant_objects_by_user(request.user)

admin.site.register(CeilometerService, CeilometerServiceAdmin)
admin.site.register(SFlowService, SFlowServiceAdmin)
admin.site.register(MonitoringChannel, MonitoringChannelAdmin)
admin.site.register(SFlowTenant, SFlowTenantAdmin)

