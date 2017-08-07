
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
from core.models import User, Deployment, Flavor

class XOSFlavor(XOSResource):
    provides = "tosca.nodes.Flavor"
    xos_model = Flavor
    copyin_props = ["flavor"]

    def get_xos_args(self):
        args = super(XOSFlavor, self).get_xos_args()

        # Support the default where the OpenStack flavor is the same as the
        # flavor name
        if "flavor" not in args:
            args["flavor"] = args["name"]

        return args

    def delete(self, obj):
        if obj.instance_set.exists():
            self.info("Flavor %s has active instances; skipping delete" % obj.name)
            return
        super(XOSFlavor, self).delete(obj)



