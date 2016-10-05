from xosresource import XOSResource
from core.models import TenantRole

class XOSTenantRole(XOSResource):
    provides = "tosca.nodes.TenantRole"
    xos_model = TenantRole
    name_field = "role"

    def get_xos_args(self):
        args = super(XOSTenantRole, self).get_xos_args()

        return args

    def delete(self, obj):
        super(XOSTenantRole, self).delete(obj)



