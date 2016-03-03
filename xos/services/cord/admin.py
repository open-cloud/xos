from django.contrib import admin

from services.cord.models import *
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
        return VOLTService.get_service_objects_by_user(request.user)

class VOLTTenantForm(forms.ModelForm):
    s_tag = forms.CharField()
    c_tag = forms.CharField()
    creator = forms.ModelChoiceField(queryset=User.objects.all())

    def __init__(self,*args,**kwargs):
        super (VOLTTenantForm,self ).__init__(*args,**kwargs)
        self.fields['kind'].widget.attrs['readonly'] = True
        self.fields['provider_service'].queryset = VOLTService.get_service_objects().all()
        if self.instance:
            # fields for the attributes
            self.fields['c_tag'].initial = self.instance.c_tag
            self.fields['s_tag'].initial = self.instance.s_tag
            self.fields['creator'].initial = self.instance.creator
        if (not self.instance) or (not self.instance.pk):
            # default fields for an 'add' form
            self.fields['kind'].initial = VOLT_KIND
            self.fields['creator'].initial = get_request().user
            if VOLTService.get_service_objects().exists():
               self.fields["provider_service"].initial = VOLTService.get_service_objects().all()[0]

    def save(self, commit=True):
        self.instance.s_tag = self.cleaned_data.get("s_tag")
        self.instance.c_tag = self.cleaned_data.get("c_tag")
        self.instance.creator = self.cleaned_data.get("creator")
        return super(VOLTTenantForm, self).save(commit=commit)

    class Meta:
        model = VOLTTenant

class VOLTTenantAdmin(ReadOnlyAwareAdmin):
    list_display = ('backend_status_icon', 'id', 'service_specific_id', 's_tag', 'c_tag', 'subscriber_root' )
    list_display_links = ('backend_status_icon', 'id')
    fieldsets = [ (None, {'fields': ['backend_status_text', 'kind', 'provider_service', 'subscriber_root', 'service_specific_id', # 'service_specific_attribute',
                                     's_tag', 'c_tag', 'creator'],
                          'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', 'service_specific_attribute')
    form = VOLTTenantForm

    suit_form_tabs = (('general','Details'),)

    def queryset(self, request):
        return VOLTTenant.get_tenant_objects_by_user(request.user)

#-----------------------------------------------------------------------------
# vCPE
#-----------------------------------------------------------------------------

class VSGServiceForm(forms.ModelForm):
    bbs_api_hostname = forms.CharField(required=False)
    bbs_api_port = forms.IntegerField(required=False)
    bbs_server = forms.CharField(required=False)
    backend_network_label = forms.CharField(required=False)
    bbs_slice = forms.ModelChoiceField(queryset=Slice.objects.all(), required=False)
    wan_container_gateway_ip = forms.CharField(required=False)
    wan_container_gateway_mac = forms.CharField(required=False)
    wan_container_netbits = forms.CharField(required=False)
    dns_servers = forms.CharField(required=False)

    def __init__(self,*args,**kwargs):
        super (VSGServiceForm,self ).__init__(*args,**kwargs)
        if self.instance:
            self.fields['bbs_api_hostname'].initial = self.instance.bbs_api_hostname
            self.fields['bbs_api_port'].initial = self.instance.bbs_api_port
            self.fields['bbs_server'].initial = self.instance.bbs_server
            self.fields['backend_network_label'].initial = self.instance.backend_network_label
            self.fields['bbs_slice'].initial = self.instance.bbs_slice
            self.fields['wan_container_gateway_ip'].initial = self.instance.wan_container_gateway_ip
            self.fields['wan_container_gateway_mac'].initial = self.instance.wan_container_gateway_mac
            self.fields['wan_container_netbits'].initial = self.instance.wan_container_netbits
            self.fields['dns_servers'].initial = self.instance.dns_servers

    def save(self, commit=True):
        self.instance.bbs_api_hostname = self.cleaned_data.get("bbs_api_hostname")
        self.instance.bbs_api_port = self.cleaned_data.get("bbs_api_port")
        self.instance.bbs_server = self.cleaned_data.get("bbs_server")
        self.instance.backend_network_label = self.cleaned_data.get("backend_network_label")
        self.instance.bbs_slice = self.cleaned_data.get("bbs_slice")
        self.instance.wan_container_gateway_ip = self.cleaned_data.get("wan_container_gateway_ip")
        self.instance.wan_container_gateway_mac = self.cleaned_data.get("wan_container_gateway_mac")
        self.instance.wan_container_netbits = self.cleaned_data.get("wan_container_netbits")
        self.instance.dns_servers = self.cleaned_data.get("dns_servers")
        return super(VSGServiceForm, self).save(commit=commit)

    class Meta:
        model = VSGService

class VSGServiceAdmin(ReadOnlyAwareAdmin):
    model = VSGService
    verbose_name = "vSG Service"
    verbose_name_plural = "vSG Service"
    list_display = ("backend_status_icon", "name", "enabled")
    list_display_links = ('backend_status_icon', 'name', )
    fieldsets = [(None,             {'fields': ['backend_status_text', 'name','enabled','versionNumber', 'description', "view_url", "icon_url", "service_specific_attribute",],
                                     'classes':['suit-tab suit-tab-general']}),
                 ("backend config", {'fields': [ "backend_network_label", "bbs_api_hostname", "bbs_api_port", "bbs_server", "bbs_slice"],
                                     'classes':['suit-tab suit-tab-backend']}),
                 ("vSG config", {'fields': [ "wan_container_gateway_ip", "wan_container_gateway_mac", "wan_container_netbits", "dns_servers"],
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

#-----------------------------------------------------------------------------
# vBNG
#-----------------------------------------------------------------------------

class VBNGServiceForm(forms.ModelForm):
    vbng_url = forms.CharField(required=False)

    def __init__(self,*args,**kwargs):
        super (VBNGServiceForm,self ).__init__(*args,**kwargs)
        if self.instance:
            self.fields['vbng_url'].initial = self.instance.vbng_url

    def save(self, commit=True):
        self.instance.vbng_url = self.cleaned_data.get("vbng_url")
        return super(VBNGServiceForm, self).save(commit=commit)

    class Meta:
        model = VBNGService

class VBNGServiceAdmin(ReadOnlyAwareAdmin):
    model = VBNGService
    verbose_name = "vBNG Service"
    verbose_name_plural = "vBNG Service"
    list_display = ("backend_status_icon", "name", "enabled")
    list_display_links = ('backend_status_icon', 'name', )
    fieldsets = [(None, {'fields': ['backend_status_text', 'name','enabled','versionNumber', 'description', "view_url", "icon_url",
                                    'vbng_url' ],
                         'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', )
    inlines = [SliceInline,ServiceAttrAsTabInline,ServicePrivilegeInline]
    form = VBNGServiceForm

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
        return VBNGService.get_service_objects_by_user(request.user)

class VBNGTenantForm(forms.ModelForm):
    routeable_subnet = forms.CharField(required=False)
    mapped_hostname = forms.CharField(required=False)
    mapped_ip = forms.CharField(required=False)
    mapped_mac =  forms.CharField(required=False)

    def __init__(self,*args,**kwargs):
        super (VBNGTenantForm,self ).__init__(*args,**kwargs)
        self.fields['kind'].widget.attrs['readonly'] = True
        self.fields['provider_service'].queryset = VBNGService.get_service_objects().all()
        if self.instance:
            # fields for the attributes
            self.fields['routeable_subnet'].initial = self.instance.routeable_subnet
            self.fields['mapped_hostname'].initial = self.instance.mapped_hostname
            self.fields['mapped_ip'].initial = self.instance.mapped_ip
            self.fields['mapped_mac'].initial = self.instance.mapped_mac
        if (not self.instance) or (not self.instance.pk):
            # default fields for an 'add' form
            self.fields['kind'].initial = VBNG_KIND
            if VBNGService.get_service_objects().exists():
               self.fields["provider_service"].initial = VBNGService.get_service_objects().all()[0]

    def save(self, commit=True):
        self.instance.routeable_subnet = self.cleaned_data.get("routeable_subnet")
        self.instance.mapped_hostname = self.cleaned_data.get("mapped_hostname")
        self.instance.mapped_ip = self.cleaned_data.get("mapped_ip")
        self.instance.mapped_mac = self.cleaned_data.get("mapped_mac")
        return super(VBNGTenantForm, self).save(commit=commit)

    class Meta:
        model = VBNGTenant

class VBNGTenantAdmin(ReadOnlyAwareAdmin):
    list_display = ('backend_status_icon', 'id', 'subscriber_tenant' )
    list_display_links = ('backend_status_icon', 'id')
    fieldsets = [ (None, {'fields': ['backend_status_text', 'kind', 'provider_service', 'subscriber_tenant', 'service_specific_id', # 'service_specific_attribute',
                                     'routeable_subnet', 'mapped_hostname', 'mapped_ip', 'mapped_mac'],
                          'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', 'service_specific_attribute')
    form = VBNGTenantForm

    suit_form_tabs = (('general','Details'),)

    def queryset(self, request):
        return VBNGTenant.get_tenant_objects_by_user(request.user)

#-----------------------------------------------------------------------------
# CordSubscriberRoot
#-----------------------------------------------------------------------------

class VOLTTenantInline(XOSTabularInline):
    model = VOLTTenant
    fields = ['provider_service', 'subscriber_root', 'service_specific_id']
    readonly_fields = ['provider_service', 'subscriber_root', 'service_specific_id']
    extra = 0
    max_num = 0
    suit_classes = 'suit-tab suit-tab-volttenants'
    fk_name = 'subscriber_root'
    verbose_name = 'subscribed tenant'
    verbose_name_plural = 'subscribed tenants'

    @property
    def selflink_reverse_path(self):
        return "admin:cord_volttenant_change"

    def queryset(self, request):
        qs = super(VOLTTenantInline, self).queryset(request)
        return qs.filter(kind=VOLT_KIND)

class CordSubscriberRootForm(forms.ModelForm):
    url_filter_level = forms.CharField(required = False)

    def __init__(self,*args,**kwargs):
        super (CordSubscriberRootForm,self ).__init__(*args,**kwargs)
        self.fields['kind'].widget.attrs['readonly'] = True
        if self.instance:
            self.fields['url_filter_level'].initial = self.instance.url_filter_level
        if (not self.instance) or (not self.instance.pk):
            # default fields for an 'add' form
            self.fields['kind'].initial = CORD_SUBSCRIBER_KIND

    def save(self, commit=True):
        self.instance.url_filter_level = self.cleaned_data.get("url_filter_level")
        return super(CordSubscriberRootForm, self).save(commit=commit)

    class Meta:
        model = CordSubscriberRoot

class CordSubscriberRootAdmin(ReadOnlyAwareAdmin):
    list_display = ('backend_status_icon', 'id',  'name', )
    list_display_links = ('backend_status_icon', 'id', 'name', )
    fieldsets = [ (None, {'fields': ['backend_status_text', 'kind', 'name', 'service_specific_id', # 'service_specific_attribute',
                                     'url_filter_level'],
                          'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', 'service_specific_attribute', 'bbs_account')
    form = CordSubscriberRootForm
    inlines = (VOLTTenantInline, TenantRootPrivilegeInline)

    suit_form_tabs =(('general', 'Cord Subscriber Root Details'),
        ('volttenants','VOLT Tenancy'),
        ('tenantrootprivileges','Privileges')
    )

    def queryset(self, request):
        return CordSubscriberRoot.get_tenant_objects_by_user(request.user)

admin.site.register(VOLTService, VOLTServiceAdmin)
admin.site.register(VOLTTenant, VOLTTenantAdmin)
admin.site.register(VSGService, VSGServiceAdmin)
admin.site.register(VSGTenant, VSGTenantAdmin)
admin.site.register(VBNGService, VBNGServiceAdmin)
admin.site.register(VBNGTenant, VBNGTenantAdmin)
admin.site.register(CordSubscriberRoot, CordSubscriberRootAdmin)

