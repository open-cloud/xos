
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
from instance_decl import *

class Instance(Instance_decl):
    class Meta:
        proxy = True

    def tologdict(self):
        d=super(Instance,self).tologdict()
        try:
            d['slice_name']=self.slice.name
            d['controller_name']=self.get_controller().name
        except:
            pass
        return d

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.slice.name
        if not self.creator and hasattr(self, 'caller'):
            self.creator = self.caller

        super(Instance, self).save(*args, **kwargs)
