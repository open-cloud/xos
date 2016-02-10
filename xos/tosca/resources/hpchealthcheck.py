import importlib
import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate
import pdb

from services.hpc.models import HpcHealthCheck, HpcService

from xosresource import XOSResource

class XOSHpcHealthCheck(XOSResource):
    provides = "tosca.nodes.HpcHealthCheck"
    xos_model = HpcHealthCheck
    name_field = None
    copyin_props = ("kind", "resource_name", "result_contains")

    def get_xos_args(self, throw_exception=True):
        args = super(XOSHpcHealthCheck, self).get_xos_args()

        service_name = self.get_requirement("tosca.relationships.MemberOfService", throw_exception=throw_exception)
        if service_name:
            args["hpcService"] = self.get_xos_object(HpcService, throw_exception=throw_exception, name=service_name)

        return args

    def get_existing_objs(self):
        args = self.get_xos_args(throw_exception=True)

        return list( HpcHealthCheck.objects.filter(hpcService=args["hpcService"], kind=args["kind"], resource_name=args["resource_name"]) )

    def postprocess(self, obj):
        pass

    def can_delete(self, obj):
        return super(XOSTenant, self).can_delete(obj)

