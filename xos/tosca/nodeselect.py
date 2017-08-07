
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


import os
import sys

from core.models import Slice,Instance,User,Flavor,Node,Image

class XOSNodeSelector(object):
    def __init__(self, user, mem_size=None, num_cpus=None, disk_size=None, hostname = None):
        self.user = user
        self.hostname = None

    def get_allowed_nodes(self):
        # TODO: logic to get nodes that the user can use
        nodes = Node.objects.all()

        if self.hostname:
            nodes = nodes.filter(name = self.hostname)

        return nodes

    def get_nodes(self, quantity):
        nodes = self.get_allowed_nodes()
        # TODO: filter out any nonfunctional nodes
        # sort by fewest number of instances
        nodes = sorted(nodes, key=lambda node: node.instances.all().count())
        return nodes[:quantity]

