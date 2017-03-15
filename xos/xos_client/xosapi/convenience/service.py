import json
from xosapi.orm import ORMWrapper, register_convenience_wrapper

class ORMWrapperService(ORMWrapper):
    @property
    def serviceattribute_dict(self):
        attrs = {}
        for attr in self.serviceattributes.all():
            attrs[attr.name] = attr.value
        return attrs

register_convenience_wrapper("Service", ORMWrapperService)
