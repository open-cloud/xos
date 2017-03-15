import json
from xosapi.orm import ORMWrapper, register_convenience_wrapper
from xosapi.convenience.service import ORMWrapperService

class ORMWrapperVRouterService(ORMWrapperService):
    def get_gateways(self):
        gateways = []

        aps = self.addresspools.all()
        for ap in aps:
            gateways.append({"gateway_ip": ap.gateway_ip, "gateway_mac": ap.gateway_mac})

        return gateways

register_convenience_wrapper("VRouterService", ORMWrapperVRouterService)
