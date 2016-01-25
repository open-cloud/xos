import time
from subprocess import PIPE, Popen

from core.admin import ReadOnlyAwareAdmin, SliceInline
from core.middleware import get_request
from core.models import User
from django import forms
from django.contrib import admin
from services.vpn.models import VPN_KIND, VPNService, VPNTenant


class VPNServiceAdmin(ReadOnlyAwareAdmin):
    """Defines the admin for the VPNService."""
    model = VPNService
    verbose_name = "VPN Service"

    list_display = ("backend_status_icon", "name", "enabled")

    list_display_links = ('backend_status_icon', 'name', )

    fieldsets = [(None, {'fields': ['backend_status_text', 'name', 'enabled',
                                    'versionNumber', 'description', "view_url"],
                         'classes':['suit-tab suit-tab-general']})]

    readonly_fields = ('backend_status_text', )

    inlines = [SliceInline]

    extracontext_registered_admins = True

    user_readonly_fields = ["name", "enabled", "versionNumber", "description"]

    suit_form_tabs = (('general', 'VPN Service Details'),
                      ('administration', 'Tenants'),
                      ('slices', 'Slices'),)

    suit_form_includes = (('vpnserviceadmin.html',
                           'top',
                           'administration'),)

    def queryset(self, request):
        return VPNService.get_service_objects_by_user(request.user)


class VPNTenantForm(forms.ModelForm):
    """The form used to create and edit a VPNTenant.

    Attributes:
        creator (forms.ModelChoiceField): The XOS user that created this tenant.
        client_conf (forms.CharField): The readonly configuration used on the client to connect to this Tenant.
        server_address (forms.GenericIPAddressField): The ip address on the VPN of this Tenant.
        client_address (forms.GenericIPAddressField): The ip address on the VPN of the client.
        is_persistent (forms.BooleanField): Determines if this Tenant keeps this connection alive through failures.
        can_view_subnet (forms.BooleanField): Determins if this Tenant makes it's subnet available to the client.

    """
    creator = forms.ModelChoiceField(queryset=User.objects.all())
    server_address = forms.GenericIPAddressField(
        protocol='IPv4', required=True)
    client_address = forms.GenericIPAddressField(
        protocol='IPv4', required=True)
    is_persistent = forms.BooleanField(required=False)
    can_view_subnet = forms.BooleanField(required=False)


    def __init__(self, *args, **kwargs):
        super(VPNTenantForm, self).__init__(*args, **kwargs)
        self.fields['kind'].widget.attrs['readonly'] = True
        # self.fields['script_name'].widget.attrs['readonly'] = True
        self.fields[
            'provider_service'].queryset = VPNService.get_service_objects().all()

        self.fields['kind'].initial = VPN_KIND

        if self.instance:
            self.fields['creator'].initial = self.instance.creator
            self.fields[
                'server_address'].initial = self.instance.server_address
            self.fields[
                'client_address'].initial = self.instance.client_address
            self.fields['is_persistent'].initial = self.instance.is_persistent
            self.fields[
                'can_view_subnet'].initial = self.instance.can_view_subnet

        if (not self.instance) or (not self.instance.pk):
            self.fields['creator'].initial = get_request().user
            self.fields['server_address'].initial = "10.8.0.1"
            self.fields['client_address'].initial = "10.8.0.2"
            self.fields['is_persistent'].initial = True
            self.fields['can_view_subnet'].initial = False
            if VPNService.get_service_objects().exists():
                self.fields["provider_service"].initial = VPNService.get_service_objects().all()[
                    0]

    def save(self, commit=True):
        self.instance.creator = self.cleaned_data.get("creator")
        self.instance.server_address = self.cleaned_data.get("server_address")
        self.instance.client_address = self.cleaned_data.get("client_address")
        self.instance.is_persistent = self.cleaned_data.get('is_persistent')
        self.instance.can_view_subnet = self.cleaned_data.get(
            'can_view_subnet')

        if self.instance.script_name == None:
            self.instance.script_name = str(time.time()) + ".vpn"

        if self.instance.server_key == None:
            self.instance.server_key = self.generate_VPN_key()

        return super(VPNTenantForm, self).save(commit=commit)

    def generate_VPN_key(self):
        """str: Generates a VPN key using the openvpn command."""
        proc = Popen("openvpn --genkey --secret /dev/stdout",
                     shell=True, stdout=PIPE)
        (stdout, stderr) = proc.communicate()
        return stdout

    class Meta:
        model = VPNTenant


class VPNTenantAdmin(ReadOnlyAwareAdmin):
    verbose_name = "VPN Tenant Admin"
    list_display = ('id', 'backend_status_icon', 'instance')
    list_display_links = ('id', 'backend_status_icon', 'instance')
    fieldsets = [(None, {'fields': ['backend_status_text', 'kind',
                                    'provider_service', 'instance', 'creator',
                                    'server_address', 'client_address',
                                    'is_persistent', 'can_view_subnet'],
                         'classes': ['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', 'instance')
    form = VPNTenantForm

    suit_form_tabs = (('general', 'Details'),)

    def queryset(self, request):
        return VPNTenant.get_tenant_objects_by_user(request.user)

# Associate the admin forms with the models.
admin.site.register(VPNService, VPNServiceAdmin)
admin.site.register(VPNTenant, VPNTenantAdmin)
