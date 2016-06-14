import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from core.models import ServiceControllerResource, ServiceController

from xosresource import XOSResource

class XOSServiceControllerResource(XOSResource):
    provides = "tosca.nodes.ServiceControllerResource"
    xos_model = ServiceControllerResource
    copyin_props = ["kind", "format", "url"]

    def get_xos_args(self, throw_exception=True):
        args = super(XOSServiceControllerResource, self).get_xos_args()

        controller_name = self.get_requirement("tosca.relationships.UsedByController", throw_exception=throw_exception)
        if controller_name:
            args["service_controller"] = self.get_xos_object(ServiceController, throw_exception=throw_exception, name=controller_name)

        return args



