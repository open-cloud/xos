from subprocess import PIPE, Popen

from django.db import transaction

from core.models import Service, TenantWithContainer
from xos.exceptions import XOSConfigurationError, XOSValidationError

OPENVPN_KIND = "openvpn"


class OpenVPNService(Service):
    """Defines the Service for creating VPN servers."""
    KIND = OPENVPN_KIND
    OPENVPN_PREFIX = "/opt/openvpn/"
    """The location of the openvpn EASY RSA files and PKIs."""
    SERVER_PREFIX = OPENVPN_PREFIX + "server-"
    """The prefix for server PKIs."""
    VARS = OPENVPN_PREFIX + "vars"
    """The location of the vars file with information for using EASY RSA."""
    EASYRSA_LOC = OPENVPN_PREFIX + "easyrsa3/easyrsa"
    """The location of the EASY RSA binary."""
    EASYRSA_COMMAND_PREFIX = EASYRSA_LOC + " --vars=" + VARS
    """Prefix for EASY RSA commands."""

    @classmethod
    def execute_easyrsa_command(cls, pki_dir, command):
        """Executes the given EASY RSA command using the given PKI.

        Parameters:
            pki_dir (str): The directory for the pki to execute the command on.
            command (str): The command to execute using ESAY RSA.
        """
        full_command = (
            OpenVPNService.EASYRSA_COMMAND_PREFIX + " --pki-dir=" +
            pki_dir + " " + command)
        proc = Popen(
            full_command, shell=True, stdout=PIPE, stderr=PIPE
        )
        (stdout, stderr) = proc.communicate()
        if (proc.returncode != 0):
            raise XOSConfigurationError(
                full_command + " failed with standard out:" + str(stdout) +
                " and stderr: " + str(stderr))

    @classmethod
    def get_pki_dir(cls, tenant):
        """Gets the directory of the PKI for the given tenant.

        Parameters:
            tenant (services.openvpn.models.OpenVPNTenant): The tenant to get the PKI directory for.

        Returns:
            str: The pki directory for the tenant.
        """
        return OpenVPNService.SERVER_PREFIX + str(tenant.id)

    class Meta:
        proxy = True
        # The name used to find this service, all directories are named this
        app_label = "openvpn"
        verbose_name = "OpenVPN Service"

    default_attributes = {'exposed_ports': None,
                          'exposed_ports_str': None}

    @property
    def exposed_ports(self):
        """Mapping[str, list(str)]: maps protocols to a list of ports for that protocol."""
        return self.get_attribute("exposed_ports",
                                  self.default_attributes["exposed_ports"])

    @exposed_ports.setter
    def exposed_ports(self, value):
        self.set_attribute("exposed_ports", value)

    @property
    def exposed_ports_str(self):
        """str: a raw str representing the exposed ports."""
        return self.get_attribute("exposed_ports_str",
                                  self.default_attributes["exposed_ports_str"])

    @exposed_ports_str.setter
    def exposed_ports_str(self, value):
        self.set_attribute("exposed_ports_str", value)

    def get_next_available_port(self, protocol):
        """Gets the next free port for the given protocol.

        Parameters:
            protocol (str): The protocol to get a port for, must be tcp or udp.

        Returns:
            int: a port number.

        Raises:
            xos.exceptions.XOSValidationError: If there the protocol is not udp or tcp.
            xos.exceptions.XOSValidationError: If there are no available ports for the protocol.
        """
        if protocol != "udp" and protocol != "tcp":
            raise XOSValidationError("Port protocol must be udp or tcp")
        if not self.exposed_ports[protocol]:
            raise XOSValidationError(
                "No availble ports for protocol: " + protocol)
        tenants = [
            tenant for tenant in OpenVPNTenant.get_tenant_objects().all()
            if tenant.protocol == protocol]
        port_numbers = self.exposed_ports[protocol]
        for port_number in port_numbers:
            if (
                len([
                    tenant for tenant in tenants
                    if tenant.port_number == port_number]) == 0):
                return port_number


class OpenVPNTenant(TenantWithContainer):
    """Defines the Tenant for creating VPN servers."""

    class Meta:
        proxy = True
        verbose_name = "OpenVPN Tenant"

    KIND = OPENVPN_KIND

    sync_attributes = ("nat_ip", "nat_mac",)

    default_attributes = {'vpn_subnet': None,
                          'server_network': None,
                          'clients_can_see_each_other': True,
                          'is_persistent': True,
                          'port': None,
                          'use_ca_from_id': None,
                          'failover_server_ids': list(),
                          'protocol': None}

    def __init__(self, *args, **kwargs):
        vpn_services = OpenVPNService.get_service_objects().all()
        if vpn_services:
            self._meta.get_field(
                "provider_service").default = vpn_services[0].id
        super(OpenVPNTenant, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        super(OpenVPNTenant, self).save(*args, **kwargs)
        model_policy_vpn_tenant(self.pk)

    def delete(self, *args, **kwargs):
        self.cleanup_container()
        super(OpenVPNTenant, self).delete(*args, **kwargs)

    @property
    def protocol(self):
        """str: The protocol that this tenant is listening on."""
        return self.get_attribute(
            "protocol", self.default_attributes["protocol"])

    @protocol.setter
    def protocol(self, value):
        self.set_attribute("protocol", value)

    @property
    def use_ca_from_id(self):
        """int: The ID of OpenVPNTenant to use to obtain a CA."""
        return self.get_attribute(
            "use_ca_from_id", self.default_attributes["use_ca_from_id"])

    @use_ca_from_id.setter
    def use_ca_from_id(self, value):
        self.set_attribute("use_ca_from_id", value)

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
    def failover_server_ids(self):
        """list(int): The IDs of the OpenVPNTenants to use as failover servers."""
        return self.get_attribute(
            "failover_server_ids", self.default_attributes["failover_server_ids"])

    @failover_server_ids.setter
    def failover_server_ids(self, value):
        self.set_attribute("failover_server_ids", value)

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
    def port_number(self):
        """int: the integer representing the port number for this server"""
        return self.get_attribute("port", self.default_attributes['port'])

    @port_number.setter
    def port_number(self, value):
        self.set_attribute("port", value)

    def get_ca_crt(self, pki_dir):
        """Gets the lines fo the ca.crt file for this OpenVPNTenant.

        Parameters:
            pki_dir (str): The PKI directory to look in.

        Returns:
            list(str): The lines of the ca.crt file for this OpenVPNTenant.
        """
        with open(pki_dir + "/ca.crt", 'r') as f:
            return f.readlines()

    def get_client_cert(self, client_name, pki_dir):
        """Gets the lines fo the crt file for a client.

        Parameters:
            pki_dir (str): The PKI directory to look in.
            client_name (str): The client name to use.

        Returns:
            list(str): The lines of the crt file for the client.
        """
        with open(pki_dir + "/issued/" + client_name + ".crt", 'r') as f:
            return f.readlines()

    def get_client_key(self, client_name, pki_dir):
        """Gets the lines fo the key file for a client.

        Parameters:
            pki_dir (str): The PKI directory to look in.
            client_name (str): The client name to use.

        Returns:
            list(str): The lines of the key file for the client.
        """
        with open(pki_dir + "/private/" + client_name + ".key", 'r') as f:
            return f.readlines()


def model_policy_vpn_tenant(pk):
    """Manages the container for the VPN Tenant.

    Parameters
        pk (int): The ID of this OpenVPNTenant.
    """
    # This section of code is atomic to prevent race conditions
    with transaction.atomic():
        # We find all of the tenants that are waiting to update
        tenant = OpenVPNTenant.objects.select_for_update().filter(pk=pk)
        if not tenant:
            return
        # Since this code is atomic it is safe to always use the first tenant
        tenant = tenant[0]
        tenant.manage_container()
