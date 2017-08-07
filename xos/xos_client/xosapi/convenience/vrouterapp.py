
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


import json
from xosapi.orm import ORMWrapper, register_convenience_wrapper

class ORMWrapperVRouterApp(ORMWrapper):
    @property
    def interfaces(self):
        app_interfaces = []
        devices = self.stub.VRouterDevice.objects.filter(vrouter_service_id=self.vrouter_service.id)
        for device in devices:
            ports = self.stub.VRouterPort.objects.filter(vrouter_device_id=device.id)
            for port in ports:
                interfaces = self.stub.VRouterInterface.objects.filter(vrouter_port_id=port.id)
                for iface in interfaces:
                    app_interfaces.append(iface.name)
        return app_interfaces

register_convenience_wrapper("VRouterApp", ORMWrapperVRouterApp)
