import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from services.hpc.models import CDNPrefix, ContentProvider

from xosresource import XOSResource

class XOSCDNPrefix(XOSResource):
    provides = "tosca.nodes.CDNPrefix"
    xos_model = CDNPrefix
    name_field = "prefix"
    copyin_props = []

    def get_xos_args(self):
        args = {"prefix": self.obj_name}

        cp_name = self.get_requirement("tosca.relationships.MemberOfContentProvider")
        if cp_name:
            args["contentProvider"] = self.get_xos_object(ContentProvider, name=cp_name)

        default_os = self.get_requirement("tosca.relationships.DefaultOriginServer")
        if default_os:
             args["defaultOriginServer"] = self.engine.name_to_xos_model(self.user, default_os)

        return args

    def can_delete(self, obj):
        return super(XOSCDNPrefix, self).can_delete(obj)

