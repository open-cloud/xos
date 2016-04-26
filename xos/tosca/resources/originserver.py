import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from services.hpc.models import OriginServer, ContentProvider

from xosresource import XOSResource

class XOSOriginServer(XOSResource):
    provides = "tosca.nodes.OriginServer"
    xos_model = OriginServer
    name_field = "url"
    copyin_props = []

    def obj_name_to_url(self):
        url = self.obj_name
        if url.startswith("http_"):
            url = url[5:]
        return url

    def get_existing_objs(self):
        url = self.obj_name_to_url()
        return self.xos_model.objects.filter(**{self.name_field: url})

    def get_xos_args(self):
        url = self.obj_name_to_url()
        cp_name = self.get_requirement("tosca.relationships.MemberOfContentProvider", throw_exception=True)
        cp = self.get_xos_object(ContentProvider, name=cp_name)
        return {"url": url,
                "contentProvider": cp}

    def can_delete(self, obj):
        return super(XOSOriginServer, self).can_delete(obj)

