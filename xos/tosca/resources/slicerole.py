from xosresource import XOSResource
from core.models import User, Deployment, SliceRole

class XOSSliceRole(XOSResource):
    provides = "tosca.nodes.SliceRole"
    xos_model = SliceRole
    name_field = "role"

    def get_xos_args(self):
        args = super(XOSSliceRole, self).get_xos_args()

        return args

    def delete(self, obj):
        super(XOSSliceRole, self).delete(obj)



