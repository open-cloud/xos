
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
import base64
from mock_modelaccessor import *
from synchronizers.new_base.syncstep import SyncStep

class SyncPort(SyncStep):
    requested_interval = 0 # 3600
    provides=[Port]
    observes=Port

    def call(self, failed=[], deletion=False):
        if deletion:
            self.delete_ports()
        else:
            self.sync_ports()

    def sync_ports(self):
        open('/tmp/sync_ports','w').write('Sync successful')
        

    def delete_ports(self):
        open('/tmp/delete_ports','w').write('Delete successful')
