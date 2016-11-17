import os
import inspect
import imp
import sys
import threading
import time
from syncstep import SyncStep
from synchronizers.base.event_loop import XOSObserver
from xos.logger import Logger, logging
from xos.config import Config
from django.utils import timezone
from diag import update_diag


watchers_enabled = getattr(Config(), "observer_enable_watchers", None)

if (watchers_enabled):
    from synchronizers.base.watchers import XOSWatcher

logger = Logger(level=logging.INFO)

class Backend:

    def load_sync_step_modules(self, step_dir=None):
        sync_steps = []
        if step_dir is None:
            try:
                step_dir = Config().observer_steps_dir
            except:
                step_dir = '/opt/xos/synchronizers/openstack/steps'


        for fn in os.listdir(step_dir):
            pathname = os.path.join(step_dir,fn)
            if os.path.isfile(pathname) and fn.endswith(".py") and (fn!="__init__.py"):
                module = imp.load_source(fn[:-3],pathname)
                for classname in dir(module):
                    c = getattr(module, classname, None)

                    # make sure 'c' is a descendent of SyncStep and has a
                    # provides field (this eliminates the abstract base classes
                    # since they don't have a provides)

                    if inspect.isclass(c) and issubclass(c, SyncStep) and hasattr(c,"provides") and (c not in sync_steps):
                        sync_steps.append(c)
        return sync_steps

    def run(self):
        update_diag(sync_start=time.time(), backend_status="0 - Synchronizer Start")

        sync_steps = self.load_sync_step_modules()

        # start the observer
        observer = XOSObserver(sync_steps)
        observer_thread = threading.Thread(target=observer.run,name='synchronizer')
        observer_thread.start()

        # start the watcher thread
        if (watchers_enabled):
            watcher = XOSWatcher(sync_steps)
            watcher_thread = threading.Thread(target=watcher.run,name='watcher')
            watcher_thread.start()

        # start model policies thread
        policies_dir = getattr(Config(), "observer_model_policies_dir", None)
        if policies_dir:
            from synchronizers.model_policy import run_policy
            model_policy_thread = threading.Thread(target=run_policy)
            model_policy_thread.start()
        else:
            model_policy_thread = None
            logger.info("Skipping model policies thread due to no model_policies dir.")

        while True:
            try:
                time.sleep(1000)
            except KeyboardInterrupt:
                print "exiting due to keyboard interrupt"
                # TODO: See about setting the threads as daemons
                observer_thread._Thread__stop()
                if model_policy_thread:
                    model_policy_thread._Thread__stop()
                sys.exit(1)

