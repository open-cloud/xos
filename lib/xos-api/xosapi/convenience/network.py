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

from __future__ import absolute_import

from xosapi.orm import (ORMLocalObjectManager, ORMWrapper,
                        register_convenience_wrapper)


class ORMWrapperNetwork(ORMWrapper):
    # slices- emulates the ManyToMany from Slice to Network via NetworkSlice
    @property
    def slices(self):
        idList = [x.slice.id for x in self.networkslices.all()]
        return ORMLocalObjectManager(self.stub, "Slice", idList, False)

    # instances- emulates the ManyToMany from Network to Instance via Port
    @property
    def instances(self):
        idList = [x.instance.id for x in self.links.all()]
        return ORMLocalObjectManager(self.stub, "Instance", idList, False)


register_convenience_wrapper("Network", ORMWrapperNetwork)
