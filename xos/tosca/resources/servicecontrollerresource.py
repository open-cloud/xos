import os
import pdb
import sys
import tempfile

from toscaparser.tosca_template import ToscaTemplate
from core.models import LoadableModuleResource, ServiceController, LoadableModule
from xosresource import XOSResource

class XOSServiceControllerResource(XOSResource):
    provides = "tosca.nodes.ServiceControllerResource"
    xos_model = LoadableModuleResource
    copyin_props = ["kind", "format", "url"]

    def get_xos_args(self, throw_exception=True):
        args = super(XOSServiceControllerResource, self).get_xos_args()

        controller_name = self.get_requirement("tosca.relationships.UsedByController", throw_exception=throw_exception)
        if controller_name:
            args["loadable_module"] = self.get_xos_object(ServiceController, throw_exception=throw_exception, name=controller_name)

        return args



