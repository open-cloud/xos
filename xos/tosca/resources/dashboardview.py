
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
from core.models import DashboardView, Site, Deployment, SiteDeployment, XOSGuiExtension

class XOSDashboardView(XOSResource):
    provides = "tosca.nodes.DashboardView"
    xos_model = DashboardView
    copyin_props = ["url", "enabled"]

    def get_xos_args(self):
        args = super(XOSDashboardView, self).get_xos_args()
        if (self.get_property("custom_icon")):
            prefix, name = self.get_property("url").split(':')
            name = name[3:]
            name = name[:1].lower() + name[1:]
            args["icon"] = "%s-icon.png" % name
            args["icon_active"] = "%s-icon-active.png" % name
        return args

    def postprocess(self, obj):
        for deployment_name in self.get_requirements("tosca.relationships.SupportsDeployment"):
            deployment = self.get_xos_object(Deployment, deployment_name)
            if not deployment in obj.deployments.all():
                print "attaching dashboardview %s to deployment %s" % (obj, deployment)
                obj.deployments.add(deployment)
                obj.save()

    def can_delete(self, obj):
        return super(XOSDashboardView, self).can_delete(obj)

    def create(self):
        xos_args = self.get_xos_args()

        dashboard = DashboardView(**xos_args)
        dashboard.save()

        self.postprocess(dashboard)

        self.info("Created DashboardView '%s'" % (str(dashboard), ))


class XOSXOSGuiExtension(XOSResource):
    provides = "tosca.nodes.XOSGuiExtension"
    xos_model = XOSGuiExtension
    copyin_props = ["name", "files"]
