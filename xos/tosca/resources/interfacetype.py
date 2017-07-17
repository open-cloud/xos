from xosresource import XOSResource
from core.models import InterfaceType

class XOSInterfaceType(XOSResource):
    provides = "tosca.nodes.InterfaceType"
    xos_model = InterfaceType
    copyin_props = ["direction"]

    def get_existing_objs(self):
        args = self.get_xos_args()
        return self.xos_model.objects.filter(**{self.name_field: self.obj_name, "direction": args["direction"]})
