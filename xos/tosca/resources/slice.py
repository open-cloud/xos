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

    def process_nodetemplate(self):
        nodetemplate = self.nodetemplate
        sliceName = nodetemplate.name

        existing_slices = Slice.objects.filter(name=sliceName)
        if existing_slices:
            self.info("Slice %s already exists" % sliceName)
            slice = existing_slices[0]
        else:
            site_name = self.get_requirement("tosca.relationships.MemberOfSite", throw_exception=True)
            site = self.get_xos_object(Site, login_base=site_name)

            slice = Slice(name = sliceName,
                          site = site)
            slice.caller = self.user
            slice.save()

            self.info("Created Slice '%s' on Site '%s'" % (str(slice), str(site)))

        self.resource = slice


    def save(self):
        self.resource.save()

