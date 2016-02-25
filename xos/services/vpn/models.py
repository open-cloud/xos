import time

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

    default_attributes = {'vpn_subnet': None,
                          'server_network': None,
                          'clients_can_see_each_other': True,
                          'is_persistent': True,
                          'script': None,
                          'ca_crt': None,
                          'port': None}

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
    def addresses(self):
        """Mapping[str, str]: The ip, mac address, and subnet of the NAT network of this Tenant."""
        if (not self.id) or (not self.instance):
            return {}

        addresses = {}
        for ns in self.instance.ports.all():
            if "nat" in ns.network.name.lower():
                addresses["ip"] = ns.ip
                addresses["mac"] = ns.mac
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
    def server_network(self):
        """str: The IP address of the server on the VPN."""
        return self.get_attribute(
            'server_network',
            self.default_attributes['server_network'])

    @server_network.setter
    def server_network(self, value):
        self.set_attribute("server_network", value)

    @property
    def vpn_subnet(self):
        """str: The IP address of the client on the VPN."""
        return self.get_attribute(
            'vpn_subnet',
            self.default_attributes['vpn_subnet'])

    @vpn_subnet.setter
    def vpn_subnet(self, value):
        self.set_attribute("vpn_subnet", value)

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
    def clients_can_see_each_other(self):
        """bool: True if the client can see the subnet of the server, false otherwise."""
        return self.get_attribute(
            "clients_can_see_each_other",
            self.default_attributes['clients_can_see_each_other'])

    @clients_can_see_each_other.setter
    def clients_can_see_each_other(self, value):
        self.set_attribute("clients_can_see_each_other", value)

    @property
    def ca_crt(self):
        """str: the string for the ca certificate"""
        return self.get_attribute("ca_crt", self.default_attributes['ca_crt'])

    @ca_crt.setter
    def ca_crt(self, value):
        self.set_attribute("ca_crt", value)

    @property
    def port_number(self):
        """int: the integer representing the port number for this server"""
        return self.get_attribute("port", self.default_attributes['port'])

    @port_number.setter
    def port_number(self, value):
        self.set_attribute("port", value)

    @property
    def script(self):
        """string: the location of the client script that is generated when
           this method is called.
        """
        script_name = time.time() + ".vpn"
        create_client_script(script_name)
        return script_name

    def create_client_script(self, script_name):
        script = open("/opt/xos/core/static/vpn/" + script_name, 'w')
        # write the configuration portion
        script.write("printf \"%b\" \"")
        for line in self.generate_client_conf().splitlines():
            script.write(line + r"\n")
        script.write("\" > client.conf\n")
        script.write("printf \"%b\" \"")
        for line in self.generate_login().splitlines():
            script.write(line + r"\n")
        script.write("\" > login.up\n")
        script.write("printf \"%b\" \"")
        for line in self.ca_crt:
            script.write(line.rstrip() + r"\n")
        script.write("\" > ca.crt\n")
        # make sure openvpn is installed
        script.write("apt-get update\n")
        script.write("apt-get install openvpn\n")
        script.write("openvpn client.conf &\n")
        # close the script
        script.close()

    def generate_login(self):
        return str(time.time()) + "\npassword\n"

    def generate_client_conf(self):
        """str: Generates the client configuration to use to connect to this VPN server.
        """
        conf = ("client\n" +
            "auth-user-pass login.up\n" +
            "dev tun\n" +
            "proto udp\n" +
            "remote " + str(self.nat_ip) + " " + str(self.port_number) + "\n" +
            "resolv-retry infinite\n" +
            "nobind\n" +
            "ca ca.crt\n" +
            "comp-lzo\n" +
            "verb 3\n")

        if self.is_persistent:
            conf += "persist-tun\n"
            conf += "persist-key\n"

        return conf



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
