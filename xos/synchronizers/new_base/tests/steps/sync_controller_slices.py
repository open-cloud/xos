
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
import syncstep
from synchronizers.new_base.ansible_helper import *
from mock_modelaccessor import *

class SyncControllerSlices(syncstep.SyncStep):
    provides=[Slice]
    requested_interval=0
    observes=ControllerSlice
    playbook='sync_controller_slices.yaml'

    def map_sync_inputs(self, controller_slice):
        if getattr(controller_slice, 'force_fail',None):
            raise Exception("Forced failure")
        elif getattr(controller_slice, 'force_defer', None):
            raise syncstep.DeferredException("Forced defer")

        tenant_fields = {'endpoint': 'endpoint',
                         'name':'Flagrant Haircut'
                         }

        return tenant_fields

    def map_sync_outputs(self, controller_slice, res):
        controller_slice.save()


    def map_delete_inputs(self, controller_slice):
        tenant_fields = {'endpoint': 'endpoint',
                          'name':'Conscientious Plastic',
                          'delete': True}
	return tenant_fields
