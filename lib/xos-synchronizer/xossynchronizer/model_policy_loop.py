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

from __future__ import absolute_import, print_function

import os
import imp
import inspect
import time
import traceback


class XOSPolicyEngine(object):
    def __init__(self, policies_dir, model_accessor, log):

        self.log = log  # has to come before self.load_model_policies(), which logs

        self.model_accessor = model_accessor
        self.model_policies = self.load_model_policies(policies_dir)
        self.policies_by_name = {}
        self.policies_by_class = {}

        for policy in self.model_policies:
            if policy.model_name not in self.policies_by_name:
                self.policies_by_name[policy.model_name] = []
            self.policies_by_name[policy.model_name].append(policy)

            if policy.model not in self.policies_by_class:
                self.policies_by_class[policy.model] = []
            self.policies_by_class[policy.model].append(policy)

    def update_wp(self, d, o):
        try:
            save_fields = []
            if d.write_protect != o.write_protect:
                d.write_protect = o.write_protect
                save_fields.append("write_protect")
            if save_fields:
                d.save(update_fields=save_fields)
        except AttributeError as e:
            raise e

    def update_dep(self, d, o):
        try:
            self.log.info("Trying to update %s", d)
            save_fields = []
            if d.updated < o.updated:
                save_fields = ["updated"]

            if save_fields:
                d.save(update_fields=save_fields)
        except AttributeError as e:
            self.log.exception("AttributeError in update_dep", e=e)
            raise e
        except Exception as e:
            self.log.exception("Exception in update_dep", e=e)

    def delete_if_inactive(self, d, o):
        try:
            d.delete()
            self.log.info("Deleted %s (%s)" % (d, d.__class__.__name__))
        except BaseException:
            pass
        return

    def load_model_policies(self, policies_dir):
        policies = []
        for fn in os.listdir(policies_dir):
            if fn.startswith("test"):
                # don't try to import unit tests!
                continue
            pathname = os.path.join(policies_dir, fn)
            if (
                os.path.isfile(pathname)
                and fn.endswith(".py")
                and (fn != "__init__.py")
            ):
                module = imp.load_source(fn[:-3], pathname)
                for classname in dir(module):
                    c = getattr(module, classname, None)

                    # make sure 'c' is a descendent of Policy and has a
                    # provides field (this eliminates the abstract base classes
                    # since they don't have a provides)

                    if inspect.isclass(c):
                        base_names = [b.__name__ for b in c.__bases__]

                        if (
                            "Policy" in base_names
                            and hasattr(c, "model_name")
                            and (c not in policies)
                        ):
                            if not c.model_name:
                                self.log.info(
                                    "load_model_policies: skipping model policy",
                                    classname=classname,
                                )
                                continue
                            if not self.model_accessor.has_model_class(c.model_name):
                                self.log.error(
                                    "load_model_policies: unable to find model policy",
                                    classname=classname,
                                    model=c.model_name,
                                )
                            c.model = self.model_accessor.get_model_class(c.model_name)
                            policies.append(c)

        self.log.info("Loaded model policies", policies=policies)
        return policies

    def execute_model_policy(self, instance, action):
        # These are the models whose children get deleted when they are
        # delete_policy_models = ["Slice", "Instance", "Network"]
        sender_name = getattr(instance, "model_name", instance.__class__.__name__)

        # if (action != "deleted"):
        #    walk_inv_deps(self.update_dep, instance)
        #    walk_deps(self.update_wp, instance)
        # elif (sender_name in delete_policy_models):
        #    walk_inv_deps(self.delete_if_inactive, instance)

        policies_failed = False
        for policy in self.policies_by_name.get(sender_name, None):
            method_name = "handle_%s" % action
            if hasattr(policy, method_name):
                try:
                    self.log.debug(
                        "MODEL POLICY: calling handler",
                        sender_name=sender_name,
                        instance=instance,
                        policy=policy.__name__,
                        method=method_name,
                    )
                    getattr(policy(model_accessor=self.model_accessor), method_name)(
                        instance
                    )
                    self.log.debug(
                        "MODEL POLICY: completed handler",
                        sender_name=sender_name,
                        instance=instance,
                        policy_name=policy.__name__,
                        method=method_name,
                    )
                except Exception as e:
                    self.log.exception("MODEL POLICY: Exception when running handler", e=e)
                    policies_failed = True

                    try:
                        instance.policy_status = "%s" % traceback.format_exc(limit=1)
                        instance.policy_code = 2
                        instance.save(update_fields=["policy_status", "policy_code"])
                    except Exception as e:
                        self.log.exception(
                            "MODEL_POLICY: Exception when storing policy_status", e=e
                        )

        if not policies_failed:
            try:
                instance.policed = max(instance.updated, instance.changed_by_step)
                instance.policy_status = "done"
                instance.policy_code = 1

                instance.save(update_fields=["policed", "policy_status", "policy_code"])

                if hasattr(policy, "after_policy_save"):
                    policy(model_accessor=self.model_accessor).after_policy_save(
                        instance
                    )

                self.log.info("MODEL_POLICY: Saved", o=instance)
            except BaseException:
                self.log.exception(
                    "MODEL POLICY: Object failed to update policed timestamp",
                    instance=instance,
                )

    def noop(self, o, p):
        pass

    def run(self):
        while True:
            start = time.time()
            try:
                self.run_policy_once()
            except Exception as e:
                self.log.exception("MODEL_POLICY: Exception in run()", e=e)
            if time.time() - start < 5:
                time.sleep(5)

    # TODO: This loop is different from the synchronizer event_loop, but they both do mostly the same thing. Look for
    # ways to combine them.

    def run_policy_once(self):
        models = list(self.policies_by_class.keys())

        self.model_accessor.check_db_connection_okay()

        objects = self.model_accessor.fetch_policies(models, False)
        deleted_objects = self.model_accessor.fetch_policies(models, True)

        for o in objects:
            if o.deleted:
                # This shouldn't happen, but previous code was examining o.deleted. Verify.
                continue
            if not o.policed:
                self.execute_model_policy(o, "create")
            else:
                self.execute_model_policy(o, "update")

        for o in deleted_objects:
            self.execute_model_policy(o, "delete")

        try:
            self.model_accessor.reset_queries()
        except Exception as e:
            # this shouldn't happen, but in case it does, catch it...
            self.log.exception("MODEL POLICY: exception in reset_queries", e)
