
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
from core.models import User, Deployment, Image

class XOSImage(XOSResource):
    provides = "tosca.nodes.Image"
    xos_model = Image
    copyin_props = ["disk_format", "container_format", "path", "kind", "tag"]

    def get_xos_args(self):
        args = super(XOSImage, self).get_xos_args()

        return args

    def create(self):
        xos_args = self.get_xos_args()

        image = Image(**xos_args)
        image.caller = self.user
        image.save()

        self.info("Created Image '%s'" % (str(image), ))

    def delete(self, obj):
        if obj.instances.exists():
            self.info("Instance %s has active instances; skipping delete" % obj.name)
            return
        super(XOSImage, self).delete(obj)



