from xosresource import XOSResource
from core.models import Service, InterfaceType, ServiceInterface

class XOSServiceInterface(XOSResource):
    provides = "tosca.nodes.ServiceInterface"
    xos_model = ServiceInterface
    copyin_props = []
    name_field = None

    def get_xos_args(self):
        args = super(XOSServiceInterface, self).get_xos_args()

        serviceName = self.get_requirement("tosca.relationships.MemberOfService", throw_exception=True)
        service = self.get_xos_object(Service, name=serviceName)
        args["service"] = service

        typeName = self.get_requirement("tosca.relationships.IsType", throw_exception=True)
        interface_type = self.get_xos_object(InterfaceType, name=typeName)
        args["interface_type"] = interface_type

        return args

    def get_existing_objs(self):
        args = self.get_xos_args()
        return self.xos_model.objects.filter(service=args["service"], interface_type=args["interface_type"])


