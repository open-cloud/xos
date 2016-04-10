from subprocess import PIPE, Popen

from core.models import Service, TenantWithContainer
from django.db import transaction
from xos.exceptions import XOSConfigurationError, XOSValidationError

VPN_KIND = "vpn"


class VPNService(Service):
    """Defines the Service for creating VPN servers."""
    KIND = VPN_KIND
    OPENVPN_PREFIX = "/opt/openvpn/"
    VARS = OPENVPN_PREFIX + "vars"
    EASYRSA_LOC = OPENVPN_PREFIX + "easyrsa3/easyrsa"
    EASYRSA_COMMAND = EASYRSA_LOC + " --vars=" + VARS

    @classmethod
    def execute_easyrsa_command(cls, pki_dir, command):
        full_command = (
            VPNService.EASYRSA_COMMAND + " --pki-dir=" +
            pki_dir + " " + command)
        proc = Popen(
            full_command, shell=True, stdout=PIPE, stderr=PIPE
        )
        (stdout, stderr) = proc.communicate()
        if (proc.returncode != 0):
            raise XOSConfigurationError(
                full_command + " failed with standard out:" + str(stdout) +
                " and stderr: " + str(stderr))

    class Meta:
        proxy = True
        # The name used to find this service, all directories are named this
        app_label = "vpn"
        verbose_name = "VPN Service"

    default_attributes = {'exposed_ports': None,
                          'exposed_ports_str': None}

    @property
    def exposed_ports(self):
        return self.get_attribute("exposed_ports",
                                  self.default_attributes["exposed_ports"])

    @exposed_ports.setter
    def exposed_ports(self, value):
        self.set_attribute("exposed_ports", value)

    @property
    def exposed_ports_str(self):
        return self.get_attribute("exposed_ports_str",
                                  self.default_attributes["exposed_ports_str"])

    @exposed_ports_str.setter
    def exposed_ports_str(self, value):
        self.set_attribute("exposed_ports_str", value)

    def get_next_available_port(self, protocol):
        if protocol != "udp" and protocol != "tcp":
            raise XOSValidationError("Port protocol must be udp or tcp")
        if not self.exposed_ports[protocol]:
            raise XOSValidationError(
                "No availble ports for protocol: " + protocol)
        tenants = [
            tenant for tenant in VPNTenant.get_tenant_objects().all()
            if tenant.protocol == protocol]
        port_numbers = self.exposed_ports[protocol]
        for port_number in port_numbers:
            if (
                len([
                    tenant for tenant in tenants
                    if tenant.port_number == port_number]) == 0):
                return port_number


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
                          'ca_crt': None,
                          'port': None,
                          'script_text': None,
                          'pki_dir': None,
                          'use_ca_from': list(),
                          'failover_servers': list(),
                          'protocol': None}

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
    def protocol(self):
        return self.get_attribute(
            "protocol", self.default_attributes["protocol"])

    @protocol.setter
    def protocol(self, value):
        self.set_attribute("protocol", value)

    @property
    def use_ca_from(self):
        return self.get_attribute(
            "use_ca_from", self.default_attributes["use_ca_from"])

    @use_ca_from.setter
    def use_ca_from(self, value):
        self.set_attribute("use_ca_from", value)

    @property
    def pki_dir(self):
        return self.get_attribute(
            "pki_dir", self.default_attributes["pki_dir"])

    @pki_dir.setter
    def pki_dir(self, value):
        self.set_attribute("pki_dir", value)

    @property
    def addresses(self):
        """Mapping[str, str]: The ip, mac address, and subnet of the NAT
            network of this Tenant."""
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
    def failover_servers(self):
        return self.get_attribute(
            "failover_servers", self.default_attributes["failover_servers"])

    @failover_servers.setter
    def failover_servers(self, value):
        self.set_attribute("failover_servers", value)

    @property
    def clients_can_see_each_other(self):
        """bool: True if the client can see the subnet of the server, false
            otherwise."""
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
    def script_text(self):
        return self.get_attribute(
            "script_text", self.default_attributes['script_text'])

    @script_text.setter
    def script_text(self, value):
        self.set_attribute("script_text", value)

    def create_client_script(self, client_name):
        script = ""
        # write the configuration portion
        script += ("printf \"%b\" \"")
        script += self.generate_client_conf(client_name)
        script += ("\" > client.conf\n")
        script += ("printf \"%b\" \"")
        for line in self.ca_crt:
            script += (line.rstrip() + r"\n")
        script += ("\" > ca.crt\n")
        script += ("printf \"%b\" \"")
        for line in self.get_client_cert(client_name):
            script += (line.rstrip() + r"\n")
        script += ("\" > " + client_name + ".crt\n")
        script += ("printf \"%b\" \"")
        for line in self.get_client_key(client_name):
            script += (line.rstrip() + r"\n")
        script += ("\" > " + client_name + ".key\n")
        # make sure openvpn is installed
        script += ("apt-get update\n")
        script += ("apt-get install openvpn\n")
        script += ("openvpn client.conf &\n")
        # close the script
        return script

    def get_client_cert(self, client_name):
        with open(self.pki_dir + "/issued/" + client_name + ".crt", 'r') as f:
            return f.readlines()

    def get_client_key(self, client_name):
        with open(self.pki_dir + "/private/" + client_name + ".key", 'r') as f:
            return f.readlines()

    def generate_client_conf(self, client_name):
        """str: Generates the client configuration to use to connect to this
            VPN server.
        """
        conf = ("client\n" +
                "dev tun\n" +
                self.get_remote_line(
                        self.nat_ip, self.port_number, self.protocol))
        for remote in self.failover_servers:
            conf += self.get_remote_line(
                    remote.nat_ip, remote.port_number, remote.protocol)

        conf += ("resolv-retry 60\n" +
                 "nobind\n" +
                 "ca ca.crt\n" +
                 "cert " + client_name + ".crt\n" +
                 "key " + client_name + ".key\n" +
                 "comp-lzo\n" +
                 "verb 3\n")

        if self.is_persistent:
            conf += "persist-tun\n"
            conf += "persist-key\n"

        return conf

    def get_remote_line(self, host, port_number, protocol):
        return ("remote " + str(host) + " " + str(port_number) + " " +
                str(protocol) + "\n")


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
