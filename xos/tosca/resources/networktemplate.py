
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
from core.models import Slice,User,Network,NetworkTemplate

class XOSNetworkTemplate(XOSResource):
    provides = "tosca.nodes.NetworkTemplate"
    xos_model = NetworkTemplate
    copyin_props = ["visibility", "translation", "shared_network_name", "shared_network_id", "toplogy_kind", "controller_kind", "access", "vtn_kind"]

    def get_xos_args(self):
        args = super(XOSNetworkTemplate, self).get_xos_args()

        return args

    def create(self):
        nodetemplate = self.nodetemplate

        xos_args = self.get_xos_args()

        networkTemplate = NetworkTemplate(**xos_args)
        networkTemplate.caller = self.user
        networkTemplate.save()

        self.info("Created NetworkTemplate '%s' " % (str(networkTemplate), ))

    def delete(self, obj):
        if obj.network_set.exists():
            return

        super(XOSNetworkTemplate, self).delete(obj)



