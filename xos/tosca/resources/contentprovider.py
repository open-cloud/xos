import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from services.hpc.models import ContentProvider, ServiceProvider

from xosresource import XOSResource

class XOSContentProvider(XOSResource):
    provides = "tosca.nodes.ContentProvider"
    xos_model = ContentProvider
    copyin_props = []

    def get_xos_args(self):
        sp_name = self.get_requirement("tosca.relationships.MemberOfServiceProvider", throw_exception=True)
        sp = self.get_xos_object(ServiceProvider, name=sp_name)
        return {"name": self.obj_name,
                "serviceProvider": sp}

    def can_delete(self, obj):
        if obj.cdnprefix_set.exists():
            self.info("%s %s has active CDN prefixes; skipping delete" % (self.xos_model.__class__, obj.name))
            return False
        return super(XOSContentProvider, self).can_delete(obj)

