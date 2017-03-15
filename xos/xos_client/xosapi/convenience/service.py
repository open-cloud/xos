import json
from xosapi.orm import ORMWrapper, register_convenience_wrapper

class ORMWrapperService(ORMWrapper):
    @property
    def serviceattribute_dict(self):
        attrs = {}
        for attr in self.serviceattributes.all():
            attrs[attr.name] = attr.value
        return attrs

    def get_composable_networks(self):
	SUPPORTED_VTN_SERVCOMP_KINDS = ['VSG','PRIVATE']

        nets = []
        for slice in self.slices.all():
            for net in slice.networks.all():
                if (net.template.vtn_kind not in SUPPORTED_VTN_SERVCOMP_KINDS) or (net.owner != slice):
                    continue

                if not net.controllernetworks.exists():
                    continue
                nets.append(net)
        return nets

register_convenience_wrapper("Service", ORMWrapperService)
