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


class ORMWrapperInstance(ORMWrapper):
    def all_ips(self):
        ips = {}
        for ns in self.ports.all():
            if ns.ip:
                ips[ns.network.name] = ns.ip
        return ips

    def all_ips_string(self):
        result = []
        ips = self.all_ips()
        for key in sorted(ips.keys()):
            # result.append("%s = %s" % (key, ips[key]))
            result.append(ips[key])
        return ", ".join(result)

    def get_public_ip(self):
        for ns in self.ports.all():
            if (
                (ns.ip)
                and (ns.network.template.visibility == "public")
                and (ns.network.template.translation == "none")
            ):
                return ns.ip
        return None

    # return an address on nat-net
    def get_network_ip(self, pattern):
        for ns in self.ports.all():
            if pattern in ns.network.name.lower():
                return ns.ip
        return None

    # return an address that the synchronizer can use to SSH to the instance
    def get_ssh_ip(self):
        # first look specifically for a management_local network
        for ns in self.ports.all():
            if (
                ns.network.template
                and ns.network.template.vtn_kind == "MANAGEMENT_LOCAL"
            ):
                return ns.ip

        # for compatibility, now look for any management network
        management = self.get_network_ip("management")
        if management:
            return management

        # if all else fails, look for nat-net (for OpenCloud?)
        return self.get_network_ip("nat")

    @property
    def controller(self):
        if self.node and self.node.site_deployment:
            return self.node.site_deployment.controller
        else:
            return None


register_convenience_wrapper("Instance", ORMWrapperInstance)
