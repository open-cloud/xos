
# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from xosresource import XOSResource
from core.models import Node, NodeLabel, Site, Deployment, SiteDeployment

class XOSNode(XOSResource):
    provides = "tosca.nodes.Node"
    xos_model = Node

    def get_xos_args(self):
        args = {"name": self.obj_name}

        site = None
        siteName = self.get_requirement("tosca.relationships.MemberOfSite", throw_exception=False)
        if siteName:
            site = self.get_xos_object(Site, login_base=siteName)

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
        for label_name in self.get_requirements("tosca.relationships.HasLabel"):
            # labels.append(self.get_xos_object(NodeLabel, name=label_name))
            label = NodeLabel.objects.get(name=label_name)
            obj.nodelabels.add(label)
            self.info("Added label '%s' for node '%s'" % (label_name, obj))

    def create(self):
        xos_args = self.get_xos_args()

        if not xos_args.get("site_deployment", None):
            raise Exception("Deployment is a required field of Node")

        node = Node(**xos_args)
        node.caller = self.user
        node.save()

        self.postprocess(node)

        self.info("Created Node '%s' on Site '%s' Deployment '%s'" % (str(node), str(node.site_deployment.site), str(node.site_deployment.deployment)))

    def delete(self, obj):
        super(XOSNode, self).delete(obj)



