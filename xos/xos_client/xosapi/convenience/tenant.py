import json
from xosapi.orm import ORMWrapper, register_convenience_wrapper

class ORMWrapperTenant(ORMWrapper):
    @property
    def tenantattribute_dict(self):
        attrs = {}
        for attr in self.tenantattributes.all():
            attrs[attr.name] = attr.value
        return attrs

register_convenience_wrapper("Tenant", ORMWrapperTenant)
