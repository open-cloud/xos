from neutron.api.v2 import attributes

FORWARD_PORTS = 'nat:forward_ports'

EXTENDED_ATTRIBUTES_2_0 = {
    'ports': {
        FORWARD_PORTS: {'allow_post': True, 'allow_put': True,
                       'default': attributes.ATTR_NOT_SPECIFIED,
                       'is_visible': True},
    }
}


class Nat(object):
    """Extension class supporting OpenCloud NAT networking

    This class is used by Quantum's extension framework to make
    metadata about the OpenCloud Port extension available to
    clients. No new resources are defined by this extension. Instead,
    the existing Port resource's request and response messages are
    extended with attributes in the OpenCloud namespace.
    """

    @classmethod
    def get_name(cls):
        return "OpenCloud NAT Networking Extension"

    @classmethod
    def get_alias(cls):
        return "nat"

    @classmethod
    def get_description(cls):
        return "Add TCP/UDP port forwarding through NAT to Quantum Port objects"

    @classmethod
    def get_namespace(cls):
        # return "http://docs.openstack.org/ext/provider/api/v1.0"
        # Nothing there right now
        return "http://www.vicci.org/ext/opencloud/nat/api/v0.1"

    @classmethod
    def get_updated(cls):
        return "2013-09-12T10:00:00-00:00"

    def get_extended_resources(self, version):
        if version == "2.0":
            return EXTENDED_ATTRIBUTES_2_0
        else:
            return {}
