from core.models import ServiceController, LoadableModule, LoadableModuleResource

from loadablemodule import XOSLoadableModule

class XOSServiceController(XOSLoadableModule):
    provides = "tosca.nodes.ServiceController"
    xos_model = ServiceController
    copyin_props = ["version", "provides", "requires", "base_url", "synchronizer_run", "synchronizer_config", "no_build", "no_deploy", "image"]

    def postprocess(self, obj):
        # allow these common resource to be specified directly by the ServiceController tosca object
        super(XOSServiceController, self).postprocess(obj)
        self.postprocess_resource_prop(obj, "synchronizer", "manifest")


