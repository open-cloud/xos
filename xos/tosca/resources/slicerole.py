
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
from core.models import User, Deployment, SliceRole

class XOSSliceRole(XOSResource):
    provides = "tosca.nodes.SliceRole"
    xos_model = SliceRole
    name_field = "role"

    def get_xos_args(self):
        args = super(XOSSliceRole, self).get_xos_args()

        return args

    def delete(self, obj):
        super(XOSSliceRole, self).delete(obj)



