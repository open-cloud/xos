
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


from xosapi.orm import ORMWrapper, register_convenience_wrapper

class ORMWrapperVSGTenant(ORMWrapper):
    sync_attributes = ("wan_container_ip", "wan_container_mac", "wan_container_netbits",
                       "wan_container_gateway_ip", "wan_container_gateway_mac",
                       "wan_vm_ip", "wan_vm_mac")

    @property
    def volt(self):
        links = self.provided_links.all()
        for link in links:
            # cast from ServiceInstance to VoltTenant
            volts = self.stub.VOLTTenant.objects.filter(id = link.subscriber_service_instance.id)
            if volts:
                return volts[0]
        return None

    @property
    def vrouter(self):
        links = self.subscribed_links.all()
        for link in links:
            # cast from ServiceInstance to VRouterTenant
            vrouters = self.stub.VRouterTenant.objects.filter(id = link.provider_service_instance.id)
            if vrouters:
                return vrouters[0]
        return None

    def get_vrouter_field(self, name, default=None):
        if self.vrouter:
            return getattr(self.vrouter, name, default)
        else:
            return default

    @property
    def wan_container_ip(self):
        return self.get_vrouter_field("public_ip", None)

    @property
    def wan_container_mac(self):
        return self.get_vrouter_field("public_mac", None)

    @property
    def wan_container_netbits(self):
        return self.get_vrouter_field("netbits", None)

    @property
    def wan_container_gateway_ip(self):
        return self.get_vrouter_field("gateway_ip", None)

    @property
    def wan_container_gateway_mac(self):
        return self.get_vrouter_field("gateway_mac", None)

    @property
    def wan_vm_ip(self):
        tags = self.stub.Tag.objects.filter(name="vm_vrouter_tenant", object_id=self.instance.id, content_type=self.instance.self_content_type_id)
        if tags:
            tenants = self.stub.VRouterTenant.objects.filter(id=int(tags[0].value))
            if not tenants:
                raise Exception("VRouterTenent %d linked to vsg %s does not exist" % (int(tags[0].value), self))
            return tenants[0].public_ip
        else:
            raise Exception("no vm_vrouter_tenant tag for instance %s" % self.instance)

    @property
    def wan_vm_mac(self):
        tags = self.stub.Tag.objects.filter(name="vm_vrouter_tenant", object_id=self.instance.id, content_type=self.instance.self_content_type_id)
        if tags:
            tenants = self.stub.VRouterTenant.objects.filter(id=int(tags[0].value))
            if not tenants:
                raise Exception("VRouterTenent %d linked to vsg %s does not exist" % (int(tags[0].value), self))
            return tenants[0].public_mac
        else:
            raise Exception("no vm_vrouter_tenant tag for instance %s" % self.instance)


register_convenience_wrapper("VSGTenant", ORMWrapperVSGTenant)
