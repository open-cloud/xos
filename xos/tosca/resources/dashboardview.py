import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from core.models import DashboardView, Site, Deployment, SiteDeployment

from xosresource import XOSResource

class XOSDashboardView(XOSResource):
    provides = "tosca.nodes.DashboardView"
    xos_model = DashboardView
    copyin_props = ["url","enabled"]

    def get_xos_args(self):
        return super(XOSDashboardView, self).get_xos_args()

    def postprocess(self, obj):
        for deployment_name in self.get_requirements("tosca.relationships.SupportsDeployment"):
            deployment = self.get_xos_object(Deployment, deployment_name)
            if not deployment in obj.deployments.all():
                print "attaching dashboardview %s to deployment %s" % (obj, deployment)
                obj.deployments.add(deployment)
                obj.save()

    def can_delete(self, obj):
        return super(XOSDashboardView, self).can_delete(obj)


