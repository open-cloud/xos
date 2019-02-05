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
from xossynchronizer.steps.syncstep import SyncStep
from mock_modelaccessor import *


class SyncRoles(SyncStep):
    requested_interval = 0

    # This observes is intentionally a list of three classes, to test steps where observes is a list of classes.
    observes = [SiteRole, SliceRole, ControllerRole]

    def sync_record(self, role):
        if not role.enacted:
            controllers = Controller.objects.all()
            for controller in controllers:
                driver = self.driver.admin_driver(controller=controller)
                driver.create_role(role.role)
            role.save()
