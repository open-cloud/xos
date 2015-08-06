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

    def get_xos_args(self):
        args = {"name": self.nodetemplate.name}

        # copy simple string properties from the template into the arguments
        for prop in ["backend_type", "version", "auth_url", "admin_user", "admin_password", "admin_tenant", "domain"]:
            v = self.get_property(prop)
            if v:
                args[prop] = v

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

    def delete(self, obj):
        if obj.controllersite.exists():
            self.info("Controller %s has active sites; skipping delete" % obj.name)
            return
        super(XOSController, self).delete(obj)



