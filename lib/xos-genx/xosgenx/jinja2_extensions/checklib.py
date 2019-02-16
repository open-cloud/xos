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
import ast


def xproto_check_synchronizer(m):
    try:
        sync_step_path = "synchronizer/steps/sync_%s.py" % m["name"].lower()
        sync_step = open(sync_step_path).read()
    except IOError:
        return "510 Model needs a sync step %s" % sync_step_path

    try:
        sync_step_ast = ast.parse(sync_step)
    except SyntaxError:
        return "511 Could not parse sync step %s" % sync_step_path

    classes = [x for x in sync_step_ast.body if isinstance(x, ast.ClassDef)]
    found_sync_step_class = False

    for c in classes:
        base_names = [v.id for v in c.bases]
        if "SyncStep" in base_names or "SyncInstanceUsingAnsible" in base_names:
            attributes = [x for x in c.body if isinstance(x, ast.Assign)]
            for a in attributes:
                target_names = [t.id for t in a.targets]
                values = a.value.elts if isinstance(a.value, ast.List) else [a.value]
                value_names = [v.id for v in values]

                if "observes" in target_names and m["name"] in value_names:
                    found_sync_step_class = True
                    break

    if not found_sync_step_class:
        return (
            "512 Synchronizer needs a sync step class with an observes field containing %s"
            % m["name"]
        )
    else:
        return "200 OK"


def xproto_check_policy(m):
    try:
        model_policy_path = (
            "synchronizer/model_policies/model_policy_%s.py" % m["name"].lower()
        )
        model_policy = open(model_policy_path).read()
    except IOError:
        return "510 Model needs a model policy %s" % model_policy_path

    try:
        model_policy_ast = ast.parse(model_policy)
    except SyntaxError:
        return "511 Could not parse sync step %s" % model_policy_path

    classes = [x for x in model_policy_ast.body if isinstance(x, ast.ClassDef)]
    found_model_policy_class = False
    for c in classes:
        base_names = [v.id for v in c.bases]
        if "Policy" in base_names or "TenantWithContainerPolicy" in base_names:
            found_model_policy_class = True
            break

    if not found_model_policy_class:
        return "513 Synchronizer needs a model policy class"
    else:
        return "200 OK"
