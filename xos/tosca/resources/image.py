from xosresource import XOSResource
from core.models import User, Deployment, Image

class XOSImage(XOSResource):
    provides = "tosca.nodes.Image"
    xos_model = Image
    copyin_props = ["disk_format", "container_format", "path", "kind", "tag"]

    def get_xos_args(self):
        args = super(XOSImage, self).get_xos_args()

        return args

    def create(self):
        xos_args = self.get_xos_args()

        image = Image(**xos_args)
        image.caller = self.user
        image.save()

        self.info("Created Image '%s'" % (str(image), ))

    def delete(self, obj):
        if obj.instances.exists():
            self.info("Instance %s has active instances; skipping delete" % obj.name)
            return
        super(XOSImage, self).delete(obj)



