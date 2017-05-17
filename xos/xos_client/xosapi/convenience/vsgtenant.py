from xosapi.orm import ORMWrapper, register_convenience_wrapper

class ORMWrapperVSGTenant(ORMWrapper):
    sync_attributes = ("wan_container_ip", "wan_container_mac", "wan_container_netbits",
                       "wan_container_gateway_ip", "wan_container_gateway_mac",
                       "wan_vm_ip", "wan_vm_mac")

    @property
    def volt(self):
        if not self.subscriber_tenant:
            return None
        # make sure subscriber_tenant is properly subclassed to a volt object
        volts = self.stub.VOLTTenant.objects.filter(id = self.subscriber_tenant.id)
        if not volts:
            return None
        return volts[0]

    @property
    def vrouter(self):
        vrouter_tenants = self.stub.VRouterTenant.objects.filter(subscriber_tenant_id = self.id)
        if vrouter_tenants:
            return vrouter_tenants[0]
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
            tenant = self.stub.VRouterTenant.objects.get(id=int(tags[0].value))
            return tenant.public_ip
        else:
            raise Exception("no vm_vrouter_tenant tag for instance %s" % self.instance)

    @property
    def wan_vm_mac(self):
        tags = self.stub.Tag.objects.filter(name="vm_vrouter_tenant", object_id=self.instance.id, content_type=self.instance.self_content_type_id)
        if tags:
            tenant = self.stub.VRouterTenant.objects.get(id=int(tags[0].value))
            return tenant.public_mac
        else:
            raise Exception("no vm_vrouter_tenant tag for instance %s" % self.instance)


register_convenience_wrapper("VSGTenant", ORMWrapperVSGTenant)
