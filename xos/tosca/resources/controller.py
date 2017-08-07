
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
from core.models import User,Controller,Deployment

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



