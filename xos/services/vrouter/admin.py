from django.contrib import admin

from services.vrouter.models import *
from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone
from django.contrib.contenttypes import generic
from suit.widgets import LinkedSelect
from core.models import AddressPool
from core.admin import ServiceAppAdmin,SliceInline,ServiceAttrAsTabInline, ReadOnlyAwareAdmin, XOSTabularInline, ServicePrivilegeInline, TenantRootTenantInline, TenantRootPrivilegeInline
from core.middleware import get_request

from functools import update_wrapper
from django.contrib.admin.views.main import ChangeList
from django.core.urlresolvers import reverse
from django.contrib.admin.utils import quote

class VRouterServiceForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super (VRouterServiceForm,self ).__init__(*args,**kwargs)

    def save(self, commit=True):
        return super(VRouterServiceForm, self).save(commit=commit)

    class Meta:
        model = VRouterService

class VRouterServiceAdmin(ReadOnlyAwareAdmin):
    model = VRouterService
    verbose_name = "vRouter Service"
    verbose_name_plural = "vRouter Service"
    list_display = ("backend_status_icon", "name", "enabled")
    list_display_links = ('backend_status_icon', 'name', )
    fieldsets = [(None, {'fields': ['backend_status_text', 'name','enabled','versionNumber', 'description', "view_url", "icon_url", ],
                         'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', )
    inlines = [SliceInline,ServiceAttrAsTabInline,ServicePrivilegeInline]
    form = VRouterServiceForm

    extracontext_registered_admins = True

    user_readonly_fields = ["name", "enabled", "versionNumber", "description"]

    suit_form_tabs =(('general', 'vRouter Service Details'),
        ('administration', 'Administration'),
        #('tools', 'Tools'),
        ('slices','Slices'),
        ('serviceattrs','Additional Attributes'),
        ('serviceprivileges','Privileges'),
    )

    suit_form_includes = (('vrouteradmin.html', 'top', 'administration'),
                           ) #('hpctools.html', 'top', 'tools') )

    def queryset(self, request):
        return VRouterService.get_service_objects_by_user(request.user)

class VRouterTenantForm(forms.ModelForm):
    public_ip = forms.CharField(required=True)
    public_mac = forms.CharField(required=True)
    gateway_ip = forms.CharField(required=False)
    gateway_mac = forms.CharField(required=False)
    cidr = forms.CharField(required=False)
    address_pool = forms.ModelChoiceField(queryset=AddressPool.objects.all(),required=False)

    def __init__(self,*args,**kwargs):
        super (VRouterTenantForm,self ).__init__(*args,**kwargs)
        self.fields['kind'].widget.attrs['readonly'] = True
        self.fields['provider_service'].queryset = VRouterService.get_service_objects().all()
        if self.instance:
            # fields for the attributes
            self.fields['address_pool'].initial = self.instance.address_pool
            self.fields['public_ip'].initial = self.instance.public_ip
            self.fields['public_mac'].initial = self.instance.public_mac
            self.fields['gateway_ip'].initial = self.instance.gateway_ip
            self.fields['gateway_mac'].initial = self.instance.gateway_mac
            self.fields['cidr'].initial = self.instance.cidr
        if (not self.instance) or (not self.instance.pk):
            # default fields for an 'add' form
            self.fields['kind'].initial = VROUTER_KIND
            if VRouterService.get_service_objects().exists():
               self.fields["provider_service"].initial = VRouterService.get_service_objects().all()[0]

    def save(self, commit=True):
        self.instance.public_ip = self.cleaned_data.get("public_ip")
        self.instance.public_mac = self.cleaned_data.get("public_mac")
        self.instance.address_pool = self.cleaned_data.get("address_pool")
        return super(VRouterTenantForm, self).save(commit=commit)

    class Meta:
        model = VRouterTenant

class VRouterTenantAdmin(ReadOnlyAwareAdmin):
    list_display = ('backend_status_icon', 'id', 'subscriber_tenant', 'public_ip' )
    list_display_links = ('backend_status_icon', 'id')
    fieldsets = [ (None, {'fields': ['backend_status_text', 'kind', 'provider_service', 'subscriber_tenant', 'subscriber_service',
                                     'address_pool', 'public_ip', 'public_mac', 'gateway_ip', 'gateway_mac', 'cidr'],
                          'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', 'service_specific_attribute', 'gateway_ip', 'gateway_mac', 'cidr')
    form = VRouterTenantForm

    suit_form_tabs = (('general','Details'),)

    def queryset(self, request):
        return VRouterTenant.get_tenant_objects_by_user(request.user)

admin.site.register(VRouterService, VRouterServiceAdmin)
admin.site.register(VRouterTenant, VRouterTenantAdmin)

