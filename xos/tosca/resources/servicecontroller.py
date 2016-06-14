import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from core.models import ServiceController, ServiceControllerResource

from xosresource import XOSResource

class XOSServiceController(XOSResource):
    provides = "tosca.nodes.ServiceController"
    xos_model = ServiceController
    copyin_props = ["base_url"]

    def postprocess_resource_prop(self, obj, kind, format):
        values = self.get_property(kind)
        if values:
            for i,value in enumerate(values.split(",")):
                value = value.strip()

                name=kind
                if i>0:
                    name = "%s_%d" %( name, i)

                scr = ServiceControllerResource.objects.filter(service_controller=obj, name=name, kind=kind, format=format)
                if scr:
                    scr=scr[0]
                    if scr.url != value:
                        self.info("updating resource %s" % kind)
                        scr.url = value
                        scr.save()
                else:
                    self.info("adding resource %s" % kind)
                    scr = ServiceControllerResource(service_controller=obj, name=name, kind=kind, format=format, url=value)
                    scr.save()

    def postprocess(self, obj):
        # allow these common resource to be specified directly by the ServiceController tosca object
        self.postprocess_resource_prop(obj, "models", "python")
        self.postprocess_resource_prop(obj, "admin", "python")
        self.postprocess_resource_prop(obj, "tosca_custom_types", "yaml")
        self.postprocess_resource_prop(obj, "tosca_resource", "python")
        self.postprocess_resource_prop(obj, "synchronizer", "manifest")
        self.postprocess_resource_prop(obj, "private_key", "raw")
        self.postprocess_resource_prop(obj, "public_key", "raw")
        self.postprocess_resource_prop(obj, "rest_service", "python")
        self.postprocess_resource_prop(obj, "rest_tenant", "python")

