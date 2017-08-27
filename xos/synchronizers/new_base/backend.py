
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
import inspect
import imp
import sys
import threading
import time
from synchronizers.new_base.syncstep import SyncStep
from synchronizers.new_base.event_loop import XOSObserver
from synchronizers.new_base.model_policy_loop import XOSPolicyEngine
from synchronizers.new_base.modelaccessor import *

from xosconfig import Config
from multistructlog import create_logger

log = create_logger(Config().get('logging'))

watchers_enabled = Config.get("enable_watchers")

if (watchers_enabled):
    from synchronizers.new_base.watchers import XOSWatcher


class Backend:

    def __init__(self, log = log):
        self.log = log
        pass

    def load_sync_step_modules(self, step_dir):
        sync_steps = []

        self.log.info("Loading sync steps", step_dir = step_dir)

        for fn in os.listdir(step_dir):
            pathname = os.path.join(step_dir,fn)
            if os.path.isfile(pathname) and fn.endswith(".py") and (fn!="__init__.py"):
                module = imp.load_source(fn[:-3],pathname)

                for classname in dir(module):
                    c = getattr(module, classname, None)

                    #if classname.startswith("Sync"):
                    #    print classname, c, inspect.isclass(c), issubclass(c, SyncStep), hasattr(c,"provides")

                    # make sure 'c' is a descendent of SyncStep and has a
                    # provides field (this eliminates the abstract base classes
                    # since they don't have a provides)
                    
                    if inspect.isclass(c):
                        base_names = [b.__name__ for b in c.__bases__]
                        if ('SyncStep' in base_names or 'OpenStackSyncStep' in base_names or 'SyncInstanceUsingAnsible' in base_names) and hasattr(c,"provides") and (c not in sync_steps):
                            sync_steps.append(c)

        self.log.info("Loaded sync steps", steps = sync_steps)

        return sync_steps

    def run(self):
        observer_thread = None
        watcher_thread = None
        model_policy_thread = None

        model_accessor.update_diag(sync_start=time.time(), backend_status="Synchronizer Start")

        steps_dir = Config.get("steps_dir")
        if steps_dir:
            sync_steps = self.load_sync_step_modules(steps_dir)
            if sync_steps:
                # start the observer
                observer = XOSObserver(sync_steps, log = self.log)
                observer_thread = threading.Thread(target=observer.run,name='synchronizer')
                observer_thread.start()

                # start the watcher thread
                if (watchers_enabled):
                    watcher = XOSWatcher(sync_steps)
                    watcher_thread = threading.Thread(target=watcher.run,name='watcher')
                    watcher_thread.start()
        else:
            self.log.info("Skipping observer and watcher threads due to no steps dir.")

        # start model policies thread
        policies_dir = Config.get("model_policies_dir")
        if policies_dir:
            policy_engine = XOSPolicyEngine(policies_dir=policies_dir, log = self.log)
            model_policy_thread = threading.Thread(target=policy_engine.run, name="policy_engine")
            model_policy_thread.start()
        else:
            self.log.info("Skipping model policies thread due to no model_policies dir.")

        while True:
            try:
                time.sleep(1000)
            except KeyboardInterrupt:
                print "exiting due to keyboard interrupt"
                # TODO: See about setting the threads as daemons
                if observer_thread:
                    observer_thread._Thread__stop()
                if watcher_thread:
                    watcher_thread._Thread__stop()
                if model_policy_thread:
                    model_policy_thread._Thread__stop()
                sys.exit(1)

