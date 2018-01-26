
# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import socket
import struct

from xos.exceptions import *
from addresspool_decl import *

class AddressPool(AddressPool_decl):
    class Meta:
        proxy = True

    def expand_cidr(self, cidr):
        (network, bits) = cidr.split("/")
        network = network.strip()
        bits = int(bits.strip())

        dest = []

        netmask = (~(pow(2, 32 - bits) - 1) & 0xFFFFFFFF)

        count = pow(2, 32 - bits)
        for i in range(2, count - 1):
            ip = struct.unpack("!L", socket.inet_aton(network))[0]
            ip = ip & netmask | i
            dest.append(socket.inet_ntoa(struct.pack("!L", ip)))

        return (dest, bits)

    def save(self, *args, **kwargs):
        """
        We need to convert subnets into lists of addresses before saving
        """
        if self.addresses and "/" in self.addresses:
            original_addresses = self.addresses
            (cidr_addrs, cidr_netbits) = self.expand_cidr(self.addresses)
            self.addresses = " ".join(cidr_addrs)
            if not self.cidr:
                self.cidr = original_addresses

        super(AddressPool, self).save(*args, **kwargs)

    def get_address(self):
        with transaction.atomic():
            ap = AddressPool.objects.get(pk=self.pk)
            if ap.addresses:
                avail_ips = ap.addresses.split()
            else:
                avail_ips = []

            if ap.inuse:
                inuse_ips = ap.inuse.split()
            else:
                inuse_ips = []

            while avail_ips:
                addr = avail_ips.pop(0)

                if addr in inuse_ips:
                    # This may have happened if someone re-ran the tosca
                    # recipe and 'refilled' the AddressPool while some addresses
                    # were still in use.
                    continue

                inuse_ips.insert(0,addr)

                ap.inuse = " ".join(inuse_ips)
                ap.addresses = " ".join(avail_ips)
                ap.save()
                return addr

            addr = None
        return addr

    def put_address(self, addr):
        with transaction.atomic():
            ap = AddressPool.objects.get(pk=self.pk)
            addresses = ap.addresses or ""
            parts = addresses.split()
            if addr not in parts:
                parts.insert(0,addr)
                ap.addresses = " ".join(parts)

            inuse = ap.inuse or ""
            parts = inuse.split()
            if addr in parts:
                parts.remove(addr)
                ap.inuse = " ".join(parts)

            ap.save()


