import os
import sys
import threading
import time
from synchronizers.base.event_loop import XOSObserver
from xos.logger import Logger, logging
from xos.config import Config
from django.utils import timezone
from diag import update_diag

logger = Logger(level=logging.INFO)

class Backend:

    def run(self):
        update_diag(sync_start=time.time(), backend_status="0 - Synchronizer Start")

        # start the observer
        observer = XOSObserver()
        observer_thread = threading.Thread(target=observer.run,name='synchronizer')
        observer_thread.start()

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

