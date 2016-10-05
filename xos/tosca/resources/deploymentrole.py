from xosresource import XOSResource
from core.models import User, Deployment, DeploymentRole

class XOSDeploymentRole(XOSResource):
    provides = "tosca.nodes.DeploymentRole"
    xos_model = DeploymentRole
    name_field = "role"

    def get_xos_args(self):
        args = super(XOSDeploymentRole, self).get_xos_args()

        return args

    def delete(self, obj):
        super(XOSDeploymentRole, self).delete(obj)

