from xosresource import XOSResource
from core.models import User,Deployment,DeploymentRole,DeploymentPrivilege,Image,ImageDeployments,Flavor

class XOSDeployment(XOSResource):
    provides = "tosca.nodes.Deployment"
    xos_model = Deployment
    copyin_props = ["accessControl"]

    def get_xos_args(self):
        args = super(XOSDeployment, self).get_xos_args()

        return args

    def postprocess(self, obj):
        # Note: support for Flavors and Images is dropped

        rolemap = ( ("tosca.relationships.AdminPrivilege", "admin"), )
        self.postprocess_privileges(DeploymentRole, DeploymentPrivilege, rolemap, obj, "deployment")

    def delete(self, obj):
        if obj.sites.exists():
            self.info("Deployment %s has active sites; skipping delete" % obj.name)
            return
        for sd in obj.sitedeployments.all():
            if sd.nodes.exists():
                self.info("Deployment %s has active nodes; skipping delete" % obj.name)
                return
        #if obj.nodes.exists():
        #    self.info("Deployment %s has active nodes; skipping delete" % obj.name)
        #    return
        super(XOSDeployment, self).delete(obj)



