
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
from core.models import User,Deployment,DeploymentRole,DeploymentPrivilege,Image,ImageDeployments,Flavor

class XOSDeployment(XOSResource):
    provides = "tosca.nodes.Deployment"
    xos_model = Deployment
    copyin_props = ["accessControl"]

    def get_xos_args(self):
        args = super(XOSDeployment, self).get_xos_args()

        return args

    def postprocess(self, obj):
        # Note: support for Flavors and Images is dropped

        rolemap = ( ("tosca.relationships.AdminPrivilege", "admin"), )
        self.postprocess_privileges(DeploymentRole, 'Deployment', rolemap, obj)

    def delete(self, obj):
        if obj.sites.exists():
            self.info("Deployment %s has active sites; skipping delete" % obj.name)
            return
        for sd in obj.sitedeployments.all():
            if sd.nodes.exists():
                self.info("Deployment %s has active nodes; skipping delete" % obj.name)
                return
        #if obj.nodes.exists():
        #    self.info("Deployment %s has active nodes; skipping delete" % obj.name)
        #    return
        super(XOSDeployment, self).delete(obj)



