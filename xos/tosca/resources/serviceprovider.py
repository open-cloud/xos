import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from services.hpc.models import ServiceProvider, HpcService

from xosresource import XOSResource

class XOSServiceProvider(XOSResource):
    provides = "tosca.nodes.ServiceProvider"
    xos_model = ServiceProvider
    copyin_props = []

    def get_xos_args(self):
        hpc_service_name = self.get_requirement("tosca.relationships.MemberOfService", throw_exception=True)
        hpc_service = self.get_xos_object(HpcService, name=hpc_service_name)
        return {"name": self.obj_name,
                "hpcService": hpc_service}

    def can_delete(self, obj):
        if obj.contentprovider_set.exists():
            self.info("%s %s has active content providers; skipping delete" % (self.xos_model.__class__, obj.name))
            return False
        return super(XOSServiceProvider, self).can_delete(obj)

