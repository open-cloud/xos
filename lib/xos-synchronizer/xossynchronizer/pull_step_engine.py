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

import imp
import inspect
import os
import threading
import time

from multistructlog import create_logger
from xosconfig import Config

log = create_logger(Config().get("logging"))


class XOSPullStepScheduler:
    """ XOSPullStepThread

        A Thread for servicing pull steps. There is one event_step associated with one XOSPullStepThread.
        The thread's pull_records() function is called for every five seconds.
    """

    def __init__(self, steps, model_accessor, *args, **kwargs):
        self.steps = steps
        self.model_accessor = model_accessor

    def run(self):
        while True:
            time.sleep(5)
            self.run_once()

    def run_once(self):
        log.debug("Starting pull steps", steps=self.steps)

        threads = []
        for step in self.steps:
            thread = threading.Thread(
                target=step(model_accessor=self.model_accessor).pull_records,
                name="pull_step",
            )
            threads.append(thread)

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        log.debug("Done with pull steps", steps=self.steps)


class XOSPullStepEngine:
    """ XOSPullStepEngine

        Load pull step modules. Two methods are defined:

            load_pull_step_modules(dir) ... look for step modules in the given directory, and load objects that are
                                       descendant from PullStep.

            start() ... Launch threads to handle processing of the PullSteps. It's expected that load_step_modules()
                        will be called before start().
    """

    def __init__(self, model_accessor):
        self.model_accessor = model_accessor
        self.pull_steps = []

    def load_pull_step_modules(self, pull_step_dir):
        self.pull_steps = []
        log.info("Loading pull steps", pull_step_dir=pull_step_dir)

        # NOTE we'll load all the classes that inherit from PullStep
        for fn in os.listdir(pull_step_dir):
            pathname = os.path.join(pull_step_dir, fn)
            if (
                os.path.isfile(pathname)
                and fn.endswith(".py")
                and (fn != "__init__.py")
                and ("test" not in fn)
            ):
                event_module = imp.load_source(fn[:-3], pathname)

                for classname in dir(event_module):
                    c = getattr(event_module, classname, None)

                    if inspect.isclass(c):
                        base_names = [b.__name__ for b in c.__bases__]
                        if "PullStep" in base_names:
                            self.pull_steps.append(c)
        log.info("Loaded pull steps", steps=self.pull_steps)

    def start(self):
        log.info("Starting pull steps engine", steps=self.pull_steps)

        for step in self.pull_steps:
            sched = XOSPullStepScheduler(
                steps=self.pull_steps, model_accessor=self.model_accessor
            )
            sched.run()
