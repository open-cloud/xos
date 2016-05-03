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

from services.vtn.models import *
from services.cord.models import CordSubscriberRoot

from functools import update_wrapper
from django.contrib.admin.views.main import ChangeList
from django.core.urlresolvers import reverse
from django.contrib.admin.utils import quote

class VTNServiceForm(forms.ModelForm):
    privateGatewayMac = forms.CharField(required=False)
    localManagementIp = forms.CharField(required=False)
    ovsdbPort = forms.CharField(required=False)
    sshPort = forms.CharField(required=False)
    sshUser = forms.CharField(required=False)
    sshKeyFile = forms.CharField(required=False)
    mgmtSubnetBits = forms.CharField(required=False)
    xosEndpoint = forms.CharField(required=False)
    xosUser = forms.CharField(required=False)
    xosPassword = forms.CharField(required=False)

    def __init__(self,*args,**kwargs):
        super (VTNServiceForm,self ).__init__(*args,**kwargs)
        if self.instance:
            self.fields['privateGatewayMac'].initial = self.instance.privateGatewayMac
            self.fields['localManagementIp'].initial = self.instance.localManagementIp
            self.fields['ovsdbPort'].initial = self.instance.ovsdbPort
            self.fields['sshPort'].initial = self.instance.sshPort
            self.fields['sshUser'].initial = self.instance.sshUser
            self.fields['sshKeyFile'].initial = self.instance.sshKeyFile
            self.fields['mgmtSubnetBits'].initial = self.instance.mgmtSubnetBits
            self.fields['xosEndpoint'].initial = self.instance.xosEndpoint
            self.fields['xosUser'].initial = self.instance.xosUser
            self.fields['xosPassword'].initial = self.instance.xosPassword

    def save(self, commit=True):
        self.instance.privateGatewayMac = self.cleaned_data.get("privateGatewayMac")
        self.instance.localManagementIp = self.cleaned_data.get("localManagementIp")
        self.instance.ovsdbPort = self.cleaned_data.get("ovsdbPort")
        self.instance.sshPort = self.cleaned_data.get("sshPort")
        self.instance.sshUser = self.cleaned_data.get("sshUser")
        self.instance.sshKeyFile = self.cleaned_data.get("sshKeyFile")
        self.instance.mgmtSubnetBits = self.cleaned_data.get("mgmtSubnetBits")
        self.instance.xosEndpoint = self.cleaned_data.get("xosEndpoint")
        self.instance.xosUser = self.cleaned_data.get("xosUser")
        self.instance.xosPassword = self.cleaned_data.get("xosPassword")
        return super(VTNServiceForm, self).save(commit=commit)

    class Meta:
        model = VTNService

class VTNServiceAdmin(ReadOnlyAwareAdmin):
    model = VTNService
    form = VTNServiceForm
    verbose_name = "VTN Service"
    verbose_name_plural = "VTN Service"
    list_display = ("backend_status_icon", "name", "enabled")
    list_display_links = ('backend_status_icon', 'name', )
    fieldsets = [(None, {'fields': ['backend_status_text', 'name','enabled','versionNumber','description',"view_url","icon_url",
                                    'privateGatewayMac', 'localManagementIp', 'ovsdbPort', 'sshPort', 'sshUser', 'sshKeyFile', 'mgmtSubnetBits', 'xosEndpoint', 'xosUser', 'xosPassword' ], 'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', )
    inlines = [SliceInline,ServiceAttrAsTabInline,ServicePrivilegeInline]

    extracontext_registered_admins = True

    user_readonly_fields = ["name", "enabled", "versionNumber", "description"]

    suit_form_tabs =(('general', 'VTN Service Details'),
#        ('administration', 'Administration'),
        ('slices','Slices'),
        ('serviceattrs','Additional Attributes'),
        ('serviceprivileges','Privileges'),
    )

    suit_form_includes = ( # ('vtnadmin.html', 'top', 'administration'),
                           ) #('hpctools.html', 'top', 'tools') )

    def queryset(self, request):
        return VTNService.get_service_objects_by_user(request.user)

admin.site.register(VTNService, VTNServiceAdmin)
