from django import forms
from django.contrib import admin

from core.admin import ReadOnlyAwareAdmin, SliceInline, TenantPrivilegeInline
from core.middleware import get_request
from core.models import User
from services.openvpn.models import OPENVPN_KIND, OpenVPNService, OpenVPNTenant
from xos.exceptions import XOSValidationError


class OpenVPNServiceForm(forms.ModelForm):

    exposed_ports = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super(OpenVPNServiceForm, self).__init__(*args, **kwargs)

        if self.instance:
            self.fields['exposed_ports'].initial = (
                self.instance.exposed_ports_str)

    def save(self, commit=True):
        self.instance.exposed_ports = self.cleaned_data['exposed_ports']
        return super(OpenVPNServiceForm, self).save(commit=commit)

    def clean_exposed_ports(self):
        exposed_ports = self.cleaned_data['exposed_ports']
        self.instance.exposed_ports_str = exposed_ports
        port_mapping = {"udp": [], "tcp": []}
        parts = exposed_ports.split(",")
        for part in parts:
            part = part.strip()
            if "/" in part:
                (protocol, ports) = part.split("/", 1)
            elif " " in part:
                (protocol, ports) = part.split(None, 1)
            else:
                raise XOSValidationError(
                    'malformed port specifier %s, format example: ' +
                    '"tcp 123, tcp 201:206, udp 333"' % part)

            protocol = protocol.strip()
            ports = ports.strip()

            if not (protocol in ["udp", "tcp"]):
                raise XOSValidationError('unknown protocol %s' % protocol)

            if "-" in ports:
                port_mapping[protocol].extend(
                    self.parse_port_range(ports, "-"))
            elif ":" in ports:
                port_mapping[protocol].extend(
                    self.parse_port_range(ports, ":"))
            else:
                port_mapping[protocol].append(int(ports))

        return port_mapping

    def parse_port_range(self, port_str, split_str):
        (first, last) = port_str.split(split_str)
        first = int(first.strip())
        last = int(last.strip())
        return list(range(first, last))

    class Meta:
        model = OpenVPNService


class OpenVPNServiceAdmin(ReadOnlyAwareAdmin):
    """Defines the admin for the OpenVPNService."""
    model = OpenVPNService
    form = OpenVPNServiceForm
    verbose_name = "OpenVPN Service"

    list_display = ("backend_status_icon", "name", "enabled")

    list_display_links = ('backend_status_icon', 'name', )

    fieldsets = [(None, {'fields': ['backend_status_text', 'name', 'enabled',
                                    'versionNumber', 'description', "view_url",
                                    'exposed_ports'],
                         'classes':['suit-tab suit-tab-general']})]

    readonly_fields = ('backend_status_text', )

    inlines = [SliceInline]

    extracontext_registered_admins = True

    user_readonly_fields = ["name", "enabled", "versionNumber", "description"]

    suit_form_tabs = (('general', 'VPN Service Details'),
                      ('slices', 'Slices'),)

    def queryset(self, request):
        return OpenVPNService.get_service_objects_by_user(request.user)


class OpenVPNTenantForm(forms.ModelForm):
    """The form used to create and edit a OpenVPNTenant.

    Attributes:
        creator (forms.ModelChoiceField): The XOS user that created this
            tenant.
        server_network (forms.GenericIPAddressField): The IP address of the VPN network.
        vpn_subnet (forms.GenericIPAddressField): The subnet used by the VPN network.
        is_persistent (forms.BooleanField): Determines if this Tenant keeps
            this connection alive through failures.
        clients_can_see_each_other (forms.BooleanField): Determines if the clients on the VPN can
            communicate with each other.
        failover_servers (forms.ModelMultipleChoiceField): The other OpenVPNTenants to use as failover
            servers.
        protocol (forms.ChoiceField): The protocol to use.
        use_ca_from (forms.ModelChoiceField): Another OpenVPNTenant to use the CA of, this is a very
            hacky way to let VPNs have the same clients.
    """
    creator = forms.ModelChoiceField(queryset=User.objects.all())
    server_network = forms.GenericIPAddressField(
        protocol="IPv4", required=True)
    vpn_subnet = forms.GenericIPAddressField(protocol="IPv4", required=True)
    is_persistent = forms.BooleanField(required=False)
    clients_can_see_each_other = forms.BooleanField(required=False)
    failover_servers = forms.ModelMultipleChoiceField(
        required=False, queryset=OpenVPNTenant.get_tenant_objects())
    protocol = forms.ChoiceField(required=True, choices=[
        ("tcp", "tcp"), ("udp", "udp")])
    use_ca_from = forms.ModelChoiceField(
        queryset=OpenVPNTenant.get_tenant_objects(), required=False)

    def __init__(self, *args, **kwargs):
        super(OpenVPNTenantForm, self).__init__(*args, **kwargs)
        self.fields['kind'].widget.attrs['readonly'] = True
        self.fields['failover_servers'].widget.attrs['rows'] = 300
        self.fields[
            'provider_service'].queryset = (
                OpenVPNService.get_service_objects().all())

        self.fields['kind'].initial = OPENVPN_KIND

        if self.instance:
            self.fields['creator'].initial = self.instance.creator
            self.fields['vpn_subnet'].initial = self.instance.vpn_subnet
            self.fields[
                'server_network'].initial = self.instance.server_network
            self.fields[
                'clients_can_see_each_other'].initial = (
                    self.instance.clients_can_see_each_other)
            self.fields['is_persistent'].initial = self.instance.is_persistent
            self.initial['protocol'] = self.instance.protocol
            self.fields['failover_servers'].queryset = (
                OpenVPNTenant.get_tenant_objects().exclude(pk=self.instance.pk))
            self.initial['failover_servers'] = OpenVPNTenant.get_tenant_objects().filter(
                pk__in=self.instance.failover_server_ids)
            self.fields['use_ca_from'].queryset = (
                OpenVPNTenant.get_tenant_objects().exclude(pk=self.instance.pk))
            if (self.instance.use_ca_from_id):
                self.initial['use_ca_from'] = (
                    OpenVPNTenant.get_tenant_objects().filter(pk=self.instance.use_ca_from_id)[0])

        if (not self.instance) or (not self.instance.pk):
            self.fields['creator'].initial = get_request().user
            self.fields['vpn_subnet'].initial = "255.255.255.0"
            self.fields['server_network'].initial = "10.66.77.0"
            self.fields['clients_can_see_each_other'].initial = True
            self.fields['is_persistent'].initial = True
            self.fields['failover_servers'].queryset = (
                OpenVPNTenant.get_tenant_objects())
            if OpenVPNService.get_service_objects().exists():
                self.fields["provider_service"].initial = (
                    OpenVPNService.get_service_objects().all()[0])

    def save(self, commit=True):
        self.instance.creator = self.cleaned_data.get("creator")
        self.instance.is_persistent = self.cleaned_data.get('is_persistent')
        self.instance.vpn_subnet = self.cleaned_data.get("vpn_subnet")
        self.instance.server_network = self.cleaned_data.get('server_network')
        self.instance.clients_can_see_each_other = self.cleaned_data.get(
            'clients_can_see_each_other')

        self.instance.failover_server_ids = [
            tenant.id for tenant in self.cleaned_data.get('failover_servers')]

        # Do not aquire a new port number if the protocol hasn't changed
        if ((not self.instance.protocol) or
                (self.instance.protocol != self.cleaned_data.get("protocol"))):
            self.instance.protocol = self.cleaned_data.get("protocol")
            self.instance.port_number = (
                self.instance.provider_service.get_next_available_port(
                    self.instance.protocol))

        if (self.cleaned_data.get('use_ca_from')):
            self.instance.use_ca_from_id = self.cleaned_data.get(
                'use_ca_from').id
        else:
            self.instance.use_ca_from_id = None

        return super(OpenVPNTenantForm, self).save(commit=commit)

    class Meta:
        model = OpenVPNTenant


class OpenVPNTenantAdmin(ReadOnlyAwareAdmin):
    verbose_name = "OpenVPN Tenant Admin"
    list_display = ('id', 'backend_status_icon', 'instance',
                    'server_network', 'vpn_subnet')
    list_display_links = ('id', 'backend_status_icon',
                          'instance', 'server_network', 'vpn_subnet')
    fieldsets = [(None, {'fields': ['backend_status_text', 'kind',
                                    'provider_service', 'instance', 'creator',
                                    'server_network', 'vpn_subnet',
                                    'is_persistent', 'use_ca_from',
                                    'clients_can_see_each_other',
                                    'failover_servers', "protocol"],
                         'classes': ['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', 'instance')
    form = OpenVPNTenantForm
    inlines = [TenantPrivilegeInline]

    suit_form_tabs = (('general', 'Details'),
                      ('tenantprivileges', 'Privileges'))

    def queryset(self, request):
        return OpenVPNTenant.get_tenant_objects_by_user(request.user)


# Associate the admin forms with the models.
admin.site.register(OpenVPNService, OpenVPNServiceAdmin)
admin.site.register(OpenVPNTenant, OpenVPNTenantAdmin)
