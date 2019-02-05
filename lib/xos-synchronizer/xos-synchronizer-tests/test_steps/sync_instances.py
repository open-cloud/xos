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
from xossynchronizer.steps import ansiblesyncstep


def escape(s):
    s = s.replace("\n", r"\n").replace('"', r"\"")
    return s


class SyncInstances(ansiblesyncstep.AnsibleSyncStep):
    requested_interval = 0
    # This observes is intentionally a list of one string, to test steps where observes is a list of strings.
    observes = ["Instance"]
    playbook = "sync_instances.yaml"

    def fetch_pending(self, deletion=False):
        objs = super(SyncInstances, self).fetch_pending(deletion)
        objs = [x for x in objs if x.isolation == "vm"]
        return objs

    def map_sync_inputs(self, instance):
        inputs = {}
        metadata_update = {}

        fields = {"name": instance.name, "delete": False}
        return fields

    def map_sync_outputs(self, instance, res):
        instance.save()

    def map_delete_inputs(self, instance):
        input = {
            "endpoint": "endpoint",
            "admin_user": "admin_user",
            "admin_password": "admin_password",
            "project_name": "project_name",
            "tenant": "tenant",
            "tenant_description": "tenant_description",
            "name": instance.name,
            "ansible_tag": "ansible_tag",
            "delete": True,
        }

        return input
