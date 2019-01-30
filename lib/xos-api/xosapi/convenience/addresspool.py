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


from __future__ import absolute_import

from xosapi.orm import ORMWrapper, register_convenience_wrapper


class ORMWrapperAddressPool(ORMWrapper):
    def get_address(self):
        ap = self
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

            inuse_ips.insert(0, addr)

            ap.inuse = " ".join(inuse_ips)
            ap.addresses = " ".join(avail_ips)
            return addr

        return None

    def put_address(self, addr):
        ap = self
        addresses = ap.addresses or ""
        parts = addresses.split()
        if addr not in parts:
            parts.insert(0, addr)
            ap.addresses = " ".join(parts)

        inuse = ap.inuse or ""
        parts = inuse.split()
        if addr in parts:
            parts.remove(addr)
            ap.inuse = " ".join(parts)


register_convenience_wrapper("AddressPool", ORMWrapperAddressPool)
