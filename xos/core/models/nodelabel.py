
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
from nodelabel_decl import *

class NodeLabel(NodeLabel_decl):
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        """ Hack to allow the creation of NodeLabel objects from outside core
            until the ORM is extended with support for ManyToMany relations.
        """

        if self.name and '###' in self.name:
            from core.models import Node

            self.name, node_id_str = self.name.split('###')
            node_ids = map(int, node_id_str.split(','))

            for node_id in node_ids:
                node = Node.get(node_id)
                self.node.add(node)

        super(NodeLabel, self).save(*args, **kwargs)
