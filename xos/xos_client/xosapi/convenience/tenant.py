import json
from xosapi.orm import ORMWrapper, register_convenience_wrapper

class ORMWrapperServiceInstance(ORMWrapper):
    @property
    def serviceinstanceattribute_dict(self):
        attrs = {}
        for attr in self.service_instance_attributes.all():
            attrs[attr.name] = attr.value
        return attrs

    @property
    def tenantattribute_dict(self):
        return self.serviceinstanceattribute_dict

class ORMWrapperTenant(ORMWrapperServiceInstance):
    pass

register_convenience_wrapper("ServiceInstance", ORMWrapperServiceInstance)
