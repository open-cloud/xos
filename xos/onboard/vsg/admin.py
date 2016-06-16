from django.contrib import admin

from services.vsg.models import *
from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone
from django.contrib.contenttypes import generic
from suit.widgets import LinkedSelect
from core.admin import ServiceAppAdmin,SliceInline,ServiceAttrAsTabInline, ReadOnlyAwareAdmin, XOSTabularInline, ServicePrivilegeInline, TenantRootTenantInline, TenantRootPrivilegeInline
from core.middleware import get_request

from functools import update_wrapper
from django.contrib.admin.views.main import ChangeList
from django.core.urlresolvers import reverse
from django.contrib.admin.utils import quote

#-----------------------------------------------------------------------------
# vSG
#-----------------------------------------------------------------------------

class VSGServiceForm(forms.ModelForm):
    bbs_api_hostname = forms.CharField(required=False)
    bbs_api_port = forms.IntegerField(required=False)
    bbs_server = forms.CharField(required=False)
    backend_network_label = forms.CharField(required=False)
    bbs_slice = forms.ModelChoiceField(queryset=Slice.objects.all(), required=False)
    dns_servers = forms.CharField(required=False)
    url_filter_kind = forms.ChoiceField(choices=VSGService.URL_FILTER_KIND_CHOICES, required=False)
    node_label = forms.CharField(required=False)

    def __init__(self,*args,**kwargs):
        super (VSGServiceForm,self ).__init__(*args,**kwargs)
        if self.instance:
            self.fields['bbs_api_hostname'].initial = self.instance.bbs_api_hostname
            self.fields['bbs_api_port'].initial = self.instance.bbs_api_port
            self.fields['bbs_server'].initial = self.instance.bbs_server
            self.fields['backend_network_label'].initial = self.instance.backend_network_label
            self.fields['bbs_slice'].initial = self.instance.bbs_slice
            self.fields['dns_servers'].initial = self.instance.dns_servers
            self.fields['url_filter_kind']. initial = self.instance.url_filter_kind
            self.fields['node_label'].initial = self.instance.node_label

    def save(self, commit=True):
        self.instance.bbs_api_hostname = self.cleaned_data.get("bbs_api_hostname")
        self.instance.bbs_api_port = self.cleaned_data.get("bbs_api_port")
        self.instance.bbs_server = self.cleaned_data.get("bbs_server")
        self.instance.backend_network_label = self.cleaned_data.get("backend_network_label")
        self.instance.bbs_slice = self.cleaned_data.get("bbs_slice")
        self.instance.dns_servers = self.cleaned_data.get("dns_servers")
        self.instance.url_filter_kind = self.cleaned_data.get("url_filter_kind")
        self.instance.node_label = self.cleaned_data.get("node_label")
        return super(VSGServiceForm, self).save(commit=commit)

    class Meta:
        model = VSGService

class VSGServiceAdmin(ReadOnlyAwareAdmin):
    model = VSGService
    verbose_name = "vSG Service"
    verbose_name_plural = "vSG Service"
    list_display = ("backend_status_icon", "name", "enabled")
    list_display_links = ('backend_status_icon', 'name', )
    fieldsets = [(None,             {'fields': ['backend_status_text', 'name','enabled','versionNumber', 'description', "view_url", "icon_url", "service_specific_attribute", "node_label"],
                                     'classes':['suit-tab suit-tab-general']}),
                 ("backend config", {'fields': [ "backend_network_label", "url_filter_kind", "bbs_api_hostname", "bbs_api_port", "bbs_server", "bbs_slice"],
                                     'classes':['suit-tab suit-tab-backend']}),
                 ("vSG config", {'fields': ["dns_servers"],
                                     'classes':['suit-tab suit-tab-vsg']}) ]
    readonly_fields = ('backend_status_text', "service_specific_attribute")
    inlines = [SliceInline,ServiceAttrAsTabInline,ServicePrivilegeInline]
    form = VSGServiceForm

    extracontext_registered_admins = True

    user_readonly_fields = ["name", "enabled", "versionNumber", "description"]

    suit_form_tabs =(('general', 'Service Details'),
        ('backend', 'Backend Config'),
        ('vsg', 'vSG Config'),
        ('administration', 'Administration'),
        #('tools', 'Tools'),
        ('slices','Slices'),
        ('serviceattrs','Additional Attributes'),
        ('serviceprivileges','Privileges') ,
    )

    suit_form_includes = (('vcpeadmin.html', 'top', 'administration'),
                           ) #('hpctools.html', 'top', 'tools') )

    def queryset(self, request):
        return VSGService.get_service_objects_by_user(request.user)

class VSGTenantForm(forms.ModelForm):
    bbs_account = forms.CharField(required=False)
    creator = forms.ModelChoiceField(queryset=User.objects.all())
    instance = forms.ModelChoiceField(queryset=Instance.objects.all(),required=False)
    last_ansible_hash = forms.CharField(required=False)
    wan_container_ip = forms.CharField(required=False)
    wan_container_mac = forms.CharField(required=False)

    def __init__(self,*args,**kwargs):
        super (VSGTenantForm,self ).__init__(*args,**kwargs)
        self.fields['kind'].widget.attrs['readonly'] = True
        self.fields['provider_service'].queryset = VSGService.get_service_objects().all()
        if self.instance:
            # fields for the attributes
            self.fields['bbs_account'].initial = self.instance.bbs_account
            self.fields['creator'].initial = self.instance.creator
            self.fields['instance'].initial = self.instance.instance
            self.fields['last_ansible_hash'].initial = self.instance.last_ansible_hash
            self.fields['wan_container_ip'].initial = self.instance.wan_container_ip
            self.fields['wan_container_mac'].initial = self.instance.wan_container_mac
        if (not self.instance) or (not self.instance.pk):
            # default fields for an 'add' form
            self.fields['kind'].initial = VCPE_KIND
            self.fields['creator'].initial = get_request().user
            if VSGService.get_service_objects().exists():
               self.fields["provider_service"].initial = VSGService.get_service_objects().all()[0]

    def save(self, commit=True):
        self.instance.creator = self.cleaned_data.get("creator")
        self.instance.instance = self.cleaned_data.get("instance")
        self.instance.last_ansible_hash = self.cleaned_data.get("last_ansible_hash")
        return super(VSGTenantForm, self).save(commit=commit)

    class Meta:
        model = VSGTenant

class VSGTenantAdmin(ReadOnlyAwareAdmin):
    list_display = ('backend_status_icon', 'id', 'subscriber_tenant' )
    list_display_links = ('backend_status_icon', 'id')
    fieldsets = [ (None, {'fields': ['backend_status_text', 'kind', 'provider_service', 'subscriber_tenant', 'service_specific_id', # 'service_specific_attribute',
                                     'wan_container_ip', 'wan_container_mac', 'bbs_account', 'creator', 'instance', 'last_ansible_hash'],
                          'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', 'service_specific_attribute', 'bbs_account', 'wan_container_ip', 'wan_container_mac')
    form = VSGTenantForm

    suit_form_tabs = (('general','Details'),)

    def queryset(self, request):
        return VSGTenant.get_tenant_objects_by_user(request.user)


admin.site.register(VSGService, VSGServiceAdmin)
admin.site.register(VSGTenant, VSGTenantAdmin)

