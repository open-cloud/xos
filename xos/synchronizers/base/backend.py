import os
import sys
import threading
import time
from synchronizers.base.event_loop import XOSObserver
#from synchronizers.base.event_manager import EventListener
from xos.logger import Logger, logging
from synchronizers.model_policy import run_policy
from xos.config import Config
from django.utils import timezone
from diag import update_diag

logger = Logger(level=logging.INFO)

class Backend:

    def run(self):
        update_diag(sync_start=time.time(), backend_status="0 - Synchronizer Start")

        # start the openstack observer
        observer = XOSObserver()
        observer_thread = threading.Thread(target=observer.run,name='synchronizer')
        observer_thread.start()

        # start model policies thread
        observer_name = getattr(Config(), "observer_name", "")
        if (not observer_name):
            model_policy_thread = threading.Thread(target=run_policy)
            model_policy_thread.start()
        else:
            model_policy_thread = None
            print "Skipping model policies thread for service observer."


        # start event listene
        #event_manager = EventListener(wake_up=observer.wake_up)
        #event_manager_thread = threading.Thread(target=event_manager.run)
        #event_manager_thread.start()

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

