import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from core.models import XOS, XOSVolume

from xosresource import XOSResource

class XOSXOS(XOSResource):
    provides = "tosca.nodes.XOS"
    xos_model = XOS

class XOSVolume(XOSResource):
    provides = "tosca.nodes.XOSVolume"
    xos_model = XOSVolume
    copyin_props = ["host_path"]
    name_field = "container_path"

    def get_xos_args(self, throw_exception=True):
        args = super(XOSVolume, self).get_xos_args()

        xos_name = self.get_requirement("tosca.relationships.UsedByXOS", throw_exception=throw_exception)
        if xos_name:
            args["xos"] = self.get_xos_object(XOS, throw_exception=throw_exception, name=xos_name)

        return args
