import os
import pdb
import socket
import sys
import struct
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from core.models import AddressPool

from xosresource import XOSResource

class XOSAddressPool(XOSResource):
    provides = "tosca.nodes.AddressPool"
    xos_model = AddressPool
    copyin_props = ["addresses", "gateway_ip", "gateway_mac"]

    def expand_cidr(self, cidr):
        (network, bits) = cidr.split("/")
        network=network.strip()
        bits=int(bits.strip())

        dest = []

        netmask = (~(pow(2,32-bits)-1) & 0xFFFFFFFF)

        count = pow(2, 32-bits)
        for i in range(2, count-1):
            ip = struct.unpack("!L", socket.inet_aton(network))[0]
            ip = ip & netmask | i
            dest.append( socket.inet_ntoa(struct.pack("!L", ip)) )

        return (dest, bits)

    def get_xos_args(self):
        args = super(XOSAddressPool, self).get_xos_args()

        if "addresses" in args:
            addr = args["addresses"]
            if "," in addr:
                raise Exception("Only one cidr per AddressPool")
            if not "/" in addr:
                raise Exception("AddressPool addresses must be a cidr")
            (cidr_addrs, cidr_netbits) = self.expand_cidr(addr)
            args["addresses"] = " ".join(cidr_addrs)
            args["cidr"] = addr

#        if "addresses" in args:
#            dest = []
#            for addr in args["addresses"].split():
#                addr=addr.strip()
#                if "/" in addr:
#                    (cidr_addrs, cidr_netbits) = self.expand_cidr(addr)
#                    dest.extend(cidr_addrs)
#                else:
#                    dest.append(addr)
#            args["addresses"] = " ".join(dest)

        return args




