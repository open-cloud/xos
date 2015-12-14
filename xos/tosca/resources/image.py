# note: this module named xossite.py instead of site.py due to conflict with
#    /usr/lib/python2.7/site.py

import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from core.models import User, Deployment, Image

from xosresource import XOSResource

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



