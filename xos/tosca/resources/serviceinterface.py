
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
from core.models import Service, InterfaceType, ServiceInterface

class XOSServiceInterface(XOSResource):
    provides = "tosca.nodes.ServiceInterface"
    xos_model = ServiceInterface
    copyin_props = []
    name_field = None

    def get_xos_args(self):
        args = super(XOSServiceInterface, self).get_xos_args()

        serviceName = self.get_requirement("tosca.relationships.MemberOfService", throw_exception=True)
        service = self.get_xos_object(Service, name=serviceName)
        args["service"] = service

        typeName = self.get_requirement("tosca.relationships.IsType", throw_exception=True)
        interface_type = self.get_xos_object(InterfaceType, name=typeName)
        args["interface_type"] = interface_type

        return args

    def get_existing_objs(self):
        args = self.get_xos_args()
        return self.xos_model.objects.filter(service=args["service"], interface_type=args["interface_type"])


