
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
    
    def is_address_manager_service_instance(self, si):
        # TODO: hardcoded dependency
        # TODO: VRouterTenant is deprecated
        return si.leaf_model_name in ["AddressManagerServiceInstance", "VRouterTenant"]

    # DEPRECATED
    @property
    def vrouter(self):
        return self.address_service_instance

    @property
    def address_service_instance(self):
        links = self.subscribed_links.all()
        for link in links:
            if not self.is_address_manager_service_instance(link.provider_service_instance):
                continue
            # cast from ServiceInstance to AddressManagerServiceInstance or similar
            return link.provider_service_instance.leaf_model
        return None

    def get_address_service_instance_field(self, name, default=None):
        if self.address_service_instance:
            return getattr(self.address_service_instance, name, default)
        else:
            return default

    @property
    def wan_container_ip(self):
        return self.get_address_service_instance_field("public_ip", None)

    @property
    def wan_container_mac(self):
        return self.get_address_service_instance_field("public_mac", None)

    @property
    def wan_container_netbits(self):
        return self.get_address_service_instance_field("netbits", None)

    @property
    def wan_container_gateway_ip(self):
        return self.get_address_service_instance_field("gateway_ip", None)

    @property
    def wan_container_gateway_mac(self):
        return self.get_address_service_instance_field("gateway_mac", None)

    @property
    def wan_vm_ip(self):
        tags = self.stub.Tag.objects.filter(name="vm_vrouter_tenant", object_id=self.instance.id, content_type=self.instance.self_content_type_id)
        if tags:
            service_instances = self.stub.ServiceInstance.objects.filter(id=int(tags[0].value))
            if not service_instances:
                raise Exception("ServiceInstance %d linked to vsg %s does not exist" % (int(tags[0].value), self))
            return service_instances[0].leaf_model.public_ip
        else:
            raise Exception("no vm_vrouter_tenant tag for instance %s" % self.instance)

    @property
    def wan_vm_mac(self):
        tags = self.stub.Tag.objects.filter(name="vm_vrouter_tenant", object_id=self.instance.id, content_type=self.instance.self_content_type_id)
        if tags:
            service_instances = self.stub.ServiceInstance.objects.filter(id=int(tags[0].value))
            if not service_instances:
                raise Exception("ServiceInstance %d linked to vsg %s does not exist" % (int(tags[0].value), self))
            return service_instances[0].leaf_model.public_mac
        else:
            raise Exception("no vm_vrouter_tenant tag for instance %s" % self.instance)


register_convenience_wrapper("VSGTenant", ORMWrapperVSGTenant)
