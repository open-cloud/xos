
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

from xos.exceptions import *
from port_decl import *

class Port(Port_decl):
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if self.instance:
            if (self.instance.slice not in self.network.permitted_slices.all()) and \
                (self.instance.slice != self.network.owner) and \
                (not self.network.permit_all_slices):
                raise XOSValidationError("Slice is not allowed to connect to network")

        if self.instance and self.service_instance:
            raise XOSValidationError("Only one of (instance, service_instance) may be set,"
                                      "port=%s, network=%s, instance=%s, service_instance=%s" %
                                     (self, self.network, self.instance, self.service_instance))

        super(Port, self).save(*args, **kwargs)
