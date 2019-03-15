# Copyright 2018-present Open Networking Foundation
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

import os
import sys
from xossynchronizer.steps.syncstep import SyncStep
from xossynchronizer.modelaccessor import TestserviceServiceInstance

from xosconfig import Config
from multistructlog import create_logger

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from helpers import put_signal, wait_for_signal

log = create_logger(Config().get('logging'))


class SyncTestserviceServiceInstance(SyncStep):
    """
    SyncTestserviceServiceInstance
    Implements sync step for syncing Testservice Services
    """

    provides = [TestserviceServiceInstance]
    observes = [TestserviceServiceInstance]
    requested_interval = 0

    def sync_record(self, model):
        log.info("TEST:SYNC_START",
                 model_class=model.model_name,
                 model_name=model.name,
                 id=model.id,
                 some_integer=model.some_integer,
                 some_other_integer=model.some_other_integer)

        put_signal(log, model, "sync_start")

        if model.sync_after_policy or model.policy_during_sync:
            wait_for_signal(log, model, "policy_done")

        if model.sync_during_policy:
            wait_for_signal(log, model, "policy_start")

        if model.update_during_sync:
            model.some_integer = model.some_integer + 1
            model.save(update_fields=["some_integer"])

    def after_sync_save(self, model):
        put_signal(log, model, "sync_done")
        log.info("TEST:SYNC_DONE",
                 model_class=model.model_name,
                 model_name=model.name,
                 id=model.id,
                 some_integer=model.some_integer,
                 some_other_integer=model.some_other_integer)

    def delete_record(self, model):
        log.info("Deleting TestserviceServiceInstance",
                 object=str(model))
        # TODO: Implement delete step
