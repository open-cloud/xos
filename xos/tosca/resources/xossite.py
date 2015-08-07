# note: this module named xossite.py instead of site.py due to conflict with
#    /usr/lib/python2.7/site.py

import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from core.models import User,Site,Deployment,Controller,SiteDeployment

from xosresource import XOSResource

class XOSSite(XOSResource):
    provides = "tosca.nodes.Site"
    xos_model = Site

    def get_xos_args(self):
        display_name = self.get_property("display_name")
        if not display_name:
            display_name = self.nodetemplate.name

        args = {"login_base": self.nodetemplate.name,
                "name": display_name}

        # copy simple string properties from the template into the arguments
        for prop in ["site_url", ]:
            v = self.get_property(prop)
            if v:
                args[prop] = v

        return args

    def get_existing_objs(self):
        return self.xos_model.objects.filter(login_base = self.nodetemplate.name)

    def postprocess(self, obj):
        results = []
        for reqs in self.nodetemplate.requirements:
            for (k,v) in reqs.items():
                if (v["relationship"] == "tosca.relationships.SiteDeployment"):
                    deployment_name = v["node"]
                    deployment = self.get_xos_object(Deployment, name=deployment_name)

                    controller_name = None
                    for sd_req in v["requirements"]:
                        for (sd_req_k, sd_req_v) in sd_req.items():
                            if sd_req_v["relationship"] == "tosca.relationship.UsesController":
                                controller_name = sd_req_v["node"]
                    if not controller_name:
                        raise Exception("Controller must be specified in SiteDeployment relationship")

                    controller = self.get_xos_object(Controller, name=controller_name)

                    existing_sitedeps = SiteDeployment.objects.filter(deployment=deployment, site=obj)
                    if existing_sitedeps:
                        self.info("SiteDeployment from %s to %s already exists" % (str(obj), str(deployment)))
                    else:
                        sitedep = SiteDeployment(deployment=deployment, site=obj, controller=controller)
                        sitedep.save()
                        self.info("Created SiteDeployment from %s to %s" % (str(obj), str(deployment)))

    def create(self):
        nodetemplate = self.nodetemplate
        siteName = nodetemplate.name

        xos_args = self.get_xos_args()

        site = Site(**xos_args)
        site.caller = self.user
        site.save()

        self.postprocess(site)

        self.info("Created Site '%s'" % (str(site), ))

    def delete(self, obj):
        if obj.slices.exists():
            self.info("Site %s has active slices; skipping delete" % obj.name)
            return
        super(XOSSite, self).delete(obj)



