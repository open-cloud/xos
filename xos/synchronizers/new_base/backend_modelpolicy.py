import os
import inspect
import imp
import sys
import threading
import time
from syncstep import SyncStep
from synchronizers.new_base.event_loop import XOSObserver
from xos.logger import Logger, logging
from xosconfig import Config

watchers_enabled = Config.get("enable_watchers")

# NOTE is this used or can be removed?
if (watchers_enabled):
    from synchronizers.new_base.watchers import XOSWatcher

logger = Logger(level=logging.INFO)

class Backend:
    def run(self):
        # start model policies thread
        policies_dir = Config("model_policies_dir")
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
                if model_policy_thread:
                    model_policy_thread._Thread__stop()
                sys.exit(1)

