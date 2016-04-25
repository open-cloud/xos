# note: this module named xossite.py instead of site.py due to conflict with
#    /usr/lib/python2.7/site.py

import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from core.models import User,Deployment,DeploymentRole,DeploymentPrivilege,Image,ImageDeployments,Flavor

from xosresource import XOSResource

class XOSDeployment(XOSResource):
    provides = "tosca.nodes.Deployment"
    xos_model = Deployment
    copyin_props = ["accessControl"]

    def get_xos_args(self):
        args = super(XOSDeployment, self).get_xos_args()

        return args

    def postprocess(self, obj):
        for imageName in self.get_requirements("tosca.relationships.SupportsImage"):
            image = self.get_xos_object(Image, name=imageName)
            imageDeps = ImageDeployments.objects.filter(deployment=obj, image=image)
            if not imageDeps:
                self.info("Attached Image %s to Deployment %s" % (image, obj))
                imageDep = ImageDeployments(deployment=obj, image=image)
                imageDep.save()

        # DEPRECATED - should switch to using a requirement, so tosca can do
        # the topsort properly

        flavors = self.get_property("flavors")
        if flavors:
            flavors = flavors.split(",")
            flavors = [x.strip() for x in flavors]

            for flavor in flavors:
                flavor = self.get_xos_object(Flavor, name=flavor)
                if not flavor.deployments.filter(id=obj.id).exists():
                    self.info("Attached flavor %s to deployment %s" % (flavor, obj))
                    flavor.deployments.add(obj)
                    flavor.save()

        # The new, right way
        for flavor in self.get_requirements("tosca.relationships.SupportsFlavor"):
            flavor = self.get_xos_object(Flavor, name=flavor)
            if not flavor.deployments.filter(id=obj.id).exists():
                self.info("Attached flavor %s to deployment %s" % (flavor, obj))
                flavor.deployments.add(obj)
                flavor.save()


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



