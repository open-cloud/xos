from xosresource import XOSResource
from core.models import User, Deployment, SiteRole

class XOSSiteRole(XOSResource):
    provides = "tosca.nodes.SiteRole"
    xos_model = SiteRole
    name_field = "role"

    def get_xos_args(self):
        args = super(XOSSiteRole, self).get_xos_args()

        return args

    def delete(self, obj):
        super(XOSSiteRole, self).delete(obj)



