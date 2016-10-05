from xosresource import XOSResource
from core.models import User, Deployment, Flavor

class XOSFlavor(XOSResource):
    provides = "tosca.nodes.Flavor"
    xos_model = Flavor
    copyin_props = ["flavor"]

    def get_xos_args(self):
        args = super(XOSFlavor, self).get_xos_args()

        # Support the default where the OpenStack flavor is the same as the
        # flavor name
        if "flavor" not in args:
            args["flavor"] = args["name"]

        return args

    def delete(self, obj):
        if obj.instance_set.exists():
            self.info("Flavor %s has active instances; skipping delete" % obj.name)
            return
        super(XOSFlavor, self).delete(obj)



