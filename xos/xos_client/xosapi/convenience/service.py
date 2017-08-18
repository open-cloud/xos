
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

class ORMWrapperService(ORMWrapper):
    @property
    def serviceattribute_dict(self):
        attrs = {}
        for attr in self.serviceattributes.all():
            attrs[attr.name] = attr.value
        return attrs

    def get_composable_networks(self):
	SUPPORTED_VTN_SERVCOMP_KINDS = ['VSG','PRIVATE']

        nets = []
        for slice in self.slices.all():
            for net in slice.networks.all():
                if (net.template.vtn_kind not in SUPPORTED_VTN_SERVCOMP_KINDS) or (net.owner.id != slice.id):
                    continue

                if not net.controllernetworks.exists():
                    continue
                nets.append(net)
        return nets

register_convenience_wrapper("Service", ORMWrapperService)
