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

    def can_delete(self, obj):
        return super(XOSDashboardView, self).can_delete(obj)


