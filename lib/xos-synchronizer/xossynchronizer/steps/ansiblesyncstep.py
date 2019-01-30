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

from xossynchronizer.ansible_helper import run_template

from .syncstep import SyncStep


class AnsibleSyncStep(SyncStep):
    def sync_record(self, o):
        self.log.debug("In default sync record", **o.tologdict())

        tenant_fields = self.map_sync_inputs(o)
        if tenant_fields == SyncStep.SYNC_WITHOUT_RUNNING:
            return

        main_obj = self.observes_classes[0]

        path = "".join(main_obj.__name__).lower()
        res = run_template(self.playbook, tenant_fields, path=path, object=o)

        if hasattr(self, "map_sync_outputs"):
            self.map_sync_outputs(o, res)

        self.log.debug("Finished default sync record", **o.tologdict())

    def delete_record(self, o):
        self.log.debug("In default delete record", **o.tologdict())

        # If there is no map_delete_inputs, then assume deleting a record is a no-op.
        if not hasattr(self, "map_delete_inputs"):
            return

        tenant_fields = self.map_delete_inputs(o)

        main_obj = self.observes_classes[0]

        path = "".join(main_obj.__name__).lower()

        tenant_fields["delete"] = True
        res = run_template(self.playbook, tenant_fields, path=path)

        if hasattr(self, "map_delete_outputs"):
            self.map_delete_outputs(o, res)
        else:
            # "rc" is often only returned when something bad happens, so assume that no "rc" implies a successful rc
            # of 0.
            if res[0].get("rc", 0) != 0:
                raise Exception("Nonzero rc from Ansible during delete_record")

        self.log.debug("Finished default delete record", **o.tologdict())
