# note: this module named xossite.py instead of site.py due to conflict with
#    /usr/lib/python2.7/site.py

import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from core.models import User,Deployment

from xosresource import XOSResource

class XOSDeployment(XOSResource):
    provides = "tosca.nodes.Deployment"
    xos_model = Deployment

    def get_xos_args(self):
        args = {"name": self.nodetemplate.name}

        return args

    def create(self):
        xos_args = self.get_xos_args()

        slice = Deployment(**xos_args)
        slice.caller = self.user
        slice.save()

        self.info("Created Deployment '%s'" % (str(slice), ))

    def delete(self, obj):
        if obj.sites.exists():
            self.info("Deployment %s has active sites; skipping delete" % obj.name)
            return
        #if obj.nodes.exists():
        #    self.info("Deployment %s has active nodes; skipping delete" % obj.name)
        #    return
        super(XOSDeployment, self).delete(obj)



