import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from core.models import Node, NodeLabel, Site, Deployment, SiteDeployment

from xosresource import XOSResource

class XOSNode(XOSResource):
    provides = "tosca.nodes.Node"
    xos_model = Node

    def get_xos_args(self):
        args = {"name": self.obj_name}

        site = None
        siteName = self.get_requirement("tosca.relationships.MemberOfSite", throw_exception=False)
        if siteName:
            site = self.get_xos_object(Site, login_base=siteName)
            args["site"] = site

        deploymentName = self.get_requirement("tosca.relationships.MemberOfDeployment", throw_exception=False)
        if deploymentName:
            deployment = self.get_xos_object(Deployment, name=deploymentName)

            if site:
                siteDeployment = self.get_xos_object(SiteDeployment, site=site, deployment=deployment, throw_exception=True)
                args["site_deployment"] = siteDeployment

        return args

    def postprocess(self, obj):
        # We can't set the labels when we create a Node, because they're
        # ManyToMany related, and the node doesn't exist yet.
        labels=[]
        for label_name in self.get_requirements("tosca.relationships.HasLabel"):
            labels.append(self.get_xos_object(NodeLabel, name=label_name))
        if labels:
            self.info("Updated labels for node '%s'" % obj)
            obj.labels = labels
            obj.save()

    def create(self):
        xos_args = self.get_xos_args()

        if not xos_args.get("site", None):
            raise Exception("Site is a required field of Node")
        if not xos_args.get("site_deployment", None):
            raise Exception("Deployment is a required field of Node")

        node = Node(**xos_args)
        node.caller = self.user
        node.save()

        self.postprocess(node)

        self.info("Created Node '%s' on Site '%s' Deployment '%s'" % (str(node), str(node.site), str(node.site_deployment.deployment)))

    def delete(self, obj):
        super(XOSNode, self).delete(obj)



