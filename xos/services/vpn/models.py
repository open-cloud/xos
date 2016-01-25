from core.models import Service, TenantWithContainer
from django.db import transaction

VPN_KIND = "vpn"


class VPNService(Service):
    """Defines the Service for creating VPN servers."""
    KIND = VPN_KIND

    class Meta:
        proxy = True
        # The name used to find this service, all directories are named this
        app_label = "vpn"
        verbose_name = "VPN Service"


class VPNTenant(TenantWithContainer):
    """Defines the Tenant for creating VPN servers."""

    class Meta:
        proxy = True
        verbose_name = "VPN Tenant"

    KIND = VPN_KIND

    sync_attributes = ("nat_ip", "nat_mac",)

    default_attributes = {'server_key': None,
                          'server_address': '10.8.0.1',
                          'client_address': '10.8.0.2',
                          'can_view_subnet': False,
                          'is_persistent': True,
                          'script_name': None}

    def __init__(self, *args, **kwargs):
        vpn_services = VPNService.get_service_objects().all()
        if vpn_services:
            self._meta.get_field(
                "provider_service").default = vpn_services[0].id
        super(VPNTenant, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        super(VPNTenant, self).save(*args, **kwargs)
        model_policy_vpn_tenant(self.pk)

    def delete(self, *args, **kwargs):
        self.cleanup_container()
        super(VPNTenant, self).delete(*args, **kwargs)

    @property
    def server_key(self):
        """str: The server_key used to connect to the VPN server."""
        return self.get_attribute(
            "server_key",
            self.default_attributes['server_key'])

    @server_key.setter
    def server_key(self, value):
        self.set_attribute("server_key", value)

    @property
    def addresses(self):
        """Mapping[str, str]: The ip, mac address, and subnet of the NAT network of this Tenant."""
        if (not self.id) or (not self.instance):
            return {}

        addresses = {}
        for ns in self.instance.ports.all():
            if "nat" in ns.network.name.lower():
                addresses["ip"] = ns.ip
                addresses["mac"] = ns.mac
                addresses["subnet"] = ns.network.subnet
                break

        return addresses

    # This getter is necessary because nat_ip is a sync_attribute
    @property
    def nat_ip(self):
        """str: The IP of this Tenant on the NAT network."""
        return self.addresses.get("ip", None)

    # This getter is necessary because nat_mac is a sync_attribute
    @property
    def nat_mac(self):
        """str: The MAC address of this Tenant on the NAT network."""
        return self.addresses.get("mac", None)

    @property
    def subnet(self):
        """str: The subnet of this Tenant on the NAT network."""
        return self.addresses.get("subnet", None)

    @property
    def server_address(self):
        """str: The IP address of the server on the VPN."""
        return self.get_attribute(
            'server_address',
            self.default_attributes['server_address'])

    @server_address.setter
    def server_address(self, value):
        self.set_attribute("server_address", value)

    @property
    def client_address(self):
        """str: The IP address of the client on the VPN."""
        return self.get_attribute(
            'client_address',
            self.default_attributes['client_address'])

    @client_address.setter
    def client_address(self, value):
        self.set_attribute("client_address", value)

    @property
    def is_persistent(self):
        """bool: True if the VPN connection is persistence, false otherwise."""
        return self.get_attribute(
            "is_persistent",
            self.default_attributes['is_persistent'])

    @is_persistent.setter
    def is_persistent(self, value):
        self.set_attribute("is_persistent", value)

    @property
    def can_view_subnet(self):
        """bool: True if the client can see the subnet of the server, false otherwise."""
        return self.get_attribute(
            "can_view_subnet",
            self.default_attributes['can_view_subnet'])

    @can_view_subnet.setter
    def can_view_subnet(self, value):
        self.set_attribute("can_view_subnet", value)

    @property
    def script_name(self):
        self.get_attribute("script_name", self.default_attributes['script_name'])

    @script_name.setter
    def script_name(self, value):
        self.set_attribute("script_name", value)


def model_policy_vpn_tenant(pk):
    """Manages the contain for the VPN Tenant."""
    # This section of code is atomic to prevent race conditions
    with transaction.atomic():
        # We find all of the tenants that are waiting to update
        tenant = VPNTenant.objects.select_for_update().filter(pk=pk)
        if not tenant:
            return
        # Since this code is atomic it is safe to always use the first tenant
        tenant = tenant[0]
        tenant.manage_container()
