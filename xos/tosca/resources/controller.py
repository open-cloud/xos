# note: this module named xossite.py instead of site.py due to conflict with
#    /usr/lib/python2.7/site.py

import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from core.models import User,Controller,Deployment

from xosresource import XOSResource

class XOSController(XOSResource):
    provides = "tosca.nodes.Controller"
    xos_model = Controller
    copyin_props = ["backend_type", "version", "auth_url", "admin_user", "admin_password", "admin_tenant", "domain", "rabbit_host", "rabbit_user", "rabbit_password"]

    def get_xos_args(self):
        args = super(XOSController, self).get_xos_args()

        deployment_name = self.get_requirement("tosca.relationships.ControllerDeployment")
        if deployment_name:
            args["deployment"] = self.get_xos_object(Deployment, name=deployment_name)

        return args

    def create(self):
        xos_args = self.get_xos_args()

        if not xos_args.get("deployment",None):
            raise Exception("Controller must have a deployment")

        controller = Controller(**xos_args)
        controller.caller = self.user
        controller.save()

        self.info("Created Controller '%s'" % (str(controller), ))

        self.postprocess(controller)

    def delete(self, obj):
        if obj.controllersite.exists():
            self.info("Controller %s has active sites; skipping delete" % obj.name)
            return
        for sd in obj.sitedeployments.all():
            if sd.nodes.exists():
                self.info("Controller %s has active nodes; skipping delete" % obj.name)
                return
        super(XOSController, self).delete(obj)



