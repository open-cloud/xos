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

from xossynchronizer.model_policies.policy import Policy

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from helpers import put_signal, wait_for_signal  # noqa: E402

DUP_FIELD_NAMES = ["name",
                   "some_integer",
                   "some_other_integer",
                   "optional_string",
                   "optional_string_with_default",
                   "optional_string_with_choices",
                   "optional_string_max_length",
                   "optional_string_stripped",
                   "optional_string_date",
                   "optional_string_ip",
                   "optional_string_indexed",
                   "required_string",
                   "required_bool_default_false",
                   "required_bool_default_true",
                   "optional_int",
                   "optional_int_with_default",
                   "optional_int_with_min",
                   "optional_int_with_max",
                   "required_int_with_default",
                   "optional_float",
                   "optional_float_with_default"]


class TestserviceServiceInstancePolicy(Policy):
    """
    TestserviceServiceInstancePolicy
    Implements model policy for TestserviceInstance
    """

    model_name = "TestserviceServiceInstance"

    def handle_create(self, model):
        self.logger.debug(
            "MODEL_POLICY: enter handle_create for TestserviceServiceInstance %s" %
            model.id)
        self.handle_update(model)
        # TODO: Implement creation policy, if it differs from update policy

    def handle_update(self, model):
        self.logger.info("TEST:POLICY_UPDATE_START", model_class=model.model_name, model_name=model.name, id=model.id,
                         some_integer=model.some_integer, some_other_integer=model.some_other_integer)

        put_signal(self.logger, model, "policy_start")

        if model.policy_after_sync or model.sync_during_policy:
            wait_for_signal(self.logger, model, "sync_done")

        if model.policy_during_sync:
            wait_for_signal(self.logger, model, "sync_start")

        if model.update_during_policy:
            model.some_other_integer = model.some_other_integer + 1
            model.save(update_fields=["some_other_integer"])

        if model.create_duplicate:
            dups = self.model_accessor.TestserviceDuplicateServiceInstance.objects.filter(serviceinstance_id=model.id)
            if dups:
                dup = dups[0]
            else:
                dup = self.model_accessor.TestserviceDuplicateServiceInstance(serviceinstance=model)

            for fieldname in DUP_FIELD_NAMES:
                value = getattr(model, fieldname)
                if value is not None:
                    setattr(dup, fieldname, value)

            dup.save()
        else:
            # See if one was previously created when create_duplicate was previously true. If so, delete it
            dups = self.model_accessor.TestserviceDuplicateServiceInstance.objects.filter(serviceinstance_id=model.id)
            for dup in dups:
                dup.delete()

    def after_policy_save(self, model):
        put_signal(self.logger, model, "policy_done")
        self.logger.info("TEST:POLICY_DONE", model_class=model.model_name, model_name=model.name, id=model.id,
                         some_integer=model.some_integer, some_other_integer=model.some_other_integer)

    def handle_delete(self, model):
        self.logger.debug(
            "MODEL_POLICY: enter handle_delete for TestserviceServiceInstance %s" %
            model.id)
        # TODO: Implement delete policy
