import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from core.models import Slice,User,Site

from xosresource import XOSResource

class XOSSlice(XOSResource):
    provides = "tosca.nodes.Slice"
    xos_model = Slice

    def get_xos_args(self):
        site_name = self.get_requirement("tosca.relationships.MemberOfSite", throw_exception=True)
        site = self.get_xos_object(Site, login_base=site_name)
        return {"name": self.nodetemplate.name,
                "site": site}

    def create(self):
        nodetemplate = self.nodetemplate
        sliceName = nodetemplate.name

        xos_args = self.get_xos_args()
        slice = Slice(**xos_args)
        slice.caller = self.user
        slice.save()

        self.info("Created Slice '%s' on Site '%s'" % (str(slice), str(slice.site)))


