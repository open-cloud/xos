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

import imp
import inspect
import os
import sys
import threading
import time

from multistructlog import create_logger
from xosconfig import Config
from xossynchronizer.event_engine import XOSEventEngine
from xossynchronizer.event_loop import XOSObserver
from xossynchronizer.model_policy_loop import XOSPolicyEngine
from xossynchronizer.pull_step_engine import XOSPullStepEngine

log = create_logger(Config().get("logging"))


class Backend:
    def __init__(self, model_accessor, log=log):
        self.model_accessor = model_accessor
        self.log = log

    def load_sync_step_modules(self, step_dir):
        sync_steps = []

        self.log.info("Loading sync steps", step_dir=step_dir)

        for fn in os.listdir(step_dir):
            pathname = os.path.join(step_dir, fn)
            if (
                os.path.isfile(pathname)
                and fn.endswith(".py")
                and (fn != "__init__.py")
                and (not fn.startswith("test"))
            ):

                # we need to extend the path to load modules in the step_dir
                sys_path_save = sys.path
                sys.path.append(step_dir)
                module = imp.load_source(fn[:-3], pathname)

                self.log.debug("Loaded file: %s", pathname)

                # reset the original path
                sys.path = sys_path_save

                for classname in dir(module):
                    c = getattr(module, classname, None)

                    # if classname.startswith("Sync"):
                    #    print classname, c, inspect.isclass(c), issubclass(c, SyncStep), hasattr(c,"provides")

                    # make sure 'c' is a descendent of SyncStep and has a
                    # provides field (this eliminates the abstract base classes
                    # since they don't have a provides)

                    if inspect.isclass(c):
                        bases = inspect.getmro(c)
                        base_names = [b.__name__ for b in bases]
                        if (
                            ("SyncStep" in base_names)
                            and (hasattr(c, "provides") or hasattr(c, "observes"))
                            and (c not in sync_steps)
                        ):
                            sync_steps.append(c)

        self.log.info("Loaded sync steps", steps=sync_steps)

        return sync_steps

    def run(self):
        observer_thread = None
        model_policy_thread = None
        event_engine = None

        steps_dir = Config.get("steps_dir")
        if steps_dir:
            sync_steps = []

            # load sync_steps
            if steps_dir:
                sync_steps = self.load_sync_step_modules(steps_dir)

            # if we have at least one sync_step
            if len(sync_steps) > 0:
                # start the observer
                self.log.info(
                    "Starting XOSObserver",
                    sync_steps=sync_steps,
                    model_accessor=self.model_accessor,
                )
                observer = XOSObserver(sync_steps, self.model_accessor, self.log)
                observer_thread = threading.Thread(
                    target=observer.run, name="synchronizer"
                )
                observer_thread.start()

        else:
            self.log.info("Skipping observer thread due to no steps dir.")

        pull_steps_dir = Config.get("pull_steps_dir")
        if not pull_steps_dir:
            self.log.info("Skipping pull step engine due to no pull_steps_dir dir.")
        elif Config.get("desired_state") == "unload":
            self.log.info("Skipping pull steps engine due to synchronizer unloading.")
        else:
            self.log.info("Starting XOSPullStepEngine", pull_steps_dir=pull_steps_dir)
            pull_steps_engine = XOSPullStepEngine(model_accessor=self.model_accessor)
            pull_steps_engine.load_pull_step_modules(pull_steps_dir)
            pull_steps_thread = threading.Thread(
                target=pull_steps_engine.start, name="pull_step_engine"
            )
            pull_steps_thread.start()

        event_steps_dir = Config.get("event_steps_dir")
        if not event_steps_dir:
            self.log.info("Skipping event engine due to no event_steps dir.")
        elif Config.get("desired_state") == "unload":
            self.log.info("Skipping event engine due to synchronizer unloading.")
        else:
            self.log.info("Starting XOSEventEngine", event_steps_dir=event_steps_dir)
            event_engine = XOSEventEngine(
                model_accessor=self.model_accessor, log=self.log
            )
            event_engine.load_event_step_modules(event_steps_dir)
            event_engine.start()

        # start model policies thread
        policies_dir = Config.get("model_policies_dir")
        if policies_dir:
            policy_engine = XOSPolicyEngine(
                policies_dir=policies_dir,
                model_accessor=self.model_accessor,
                log=self.log,
            )
            model_policy_thread = threading.Thread(
                target=policy_engine.run, name="policy_engine"
            )
            model_policy_thread.is_policy_thread = True
            model_policy_thread.start()
        else:
            self.log.info(
                "Skipping model policies thread due to no model_policies dir."
            )

        if (not observer_thread) and (not model_policy_thread) and (not event_engine):
            self.log.info(
                "No sync steps, no policies, and no event steps. Synchronizer exiting."
            )
            # the caller will exit with status 0
            return

        while True:
            try:
                time.sleep(1000)
            except KeyboardInterrupt:
                print("exiting due to keyboard interrupt")
                # TODO: See about setting the threads as daemons
                if observer_thread:
                    observer_thread._Thread__stop()
                if model_policy_thread:
                    model_policy_thread._Thread__stop()
                sys.exit(1)
