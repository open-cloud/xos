import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from services.cord.models import VOLTDevice, VOLTService
from xosresource import XOSResource

class XOSVOLTDevice(XOSResource):
    provides = "tosca.nodes.VOLTDevice"
    xos_model = VOLTDevice
    copyin_props = ["openflow_id", "driver"]

    def get_xos_args(self, throw_exception=True):
        args = super(XOSVOLTDevice, self).get_xos_args()

        volt_service_name = self.get_requirement("tosca.relationships.MemberOfService", throw_exception=throw_exception)
        if volt_service_name:
            args["volt_service"] = self.get_xos_object(VOLTService, throw_exception=throw_exception, name=volt_service_name)

        return args
