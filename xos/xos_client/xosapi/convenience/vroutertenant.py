import json
from xosapi.orm import ORMWrapper, register_convenience_wrapper

class ORMWrapperVRouterTenant(ORMWrapper):
    # hopefully this goes away when VRouterTenant is made a real object

    def get_attribute(self, name, default=None):
        if self.service_specific_attribute:
            attributes = json.loads(self.service_specific_attribute)
        else:
            attributes = {}
        return attributes.get(name, default)

    @property
    def address_pool_id(self):
        return self.get_attribute("address_pool_id", None)

    @property
    def public_ip(self):
        return self.get_attribute("public_ip", None)

    @property
    def public_mac(self):
        return self.get_attribute("public_mac", None)

    @property
    def gateway_ip(self):
        if not self.address_pool:
            return None
        return self.address_pool.gateway_ip

    @property
    def gateway_mac(self):
        if not self.address_pool:
            return None
        return self.address_pool.gateway_mac

    @property
    def cidr(self):
        if not self.address_pool:
            return None
        return self.address_pool.cidr

    @property
    def netbits(self):
        # return number of bits in the network portion of the cidr
        if self.cidr:
            parts = self.cidr.split("/")
            if len(parts) == 2:
                return int(parts[1].strip())
        return None

    @property
    def address_pool(self):
        if not self.address_pool_id:
            return None
        aps = self.stub.AddressPool.objects.filter(id=self.address_pool_id)
        if not aps:
            return None
        ap = aps[0]
        return ap

register_convenience_wrapper("VRouterTenant", ORMWrapperVRouterTenant)
