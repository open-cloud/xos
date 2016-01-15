import threading
import time
from ec2_observer.event_loop import XOSObserver
from ec2_observer.event_manager import EventListener
from xos.logger import Logger, logging

logger = Logger(level=logging.INFO)

class Backend:
    
    def run(self):
        # start the openstack observer
        observer = XOSObserver()
        observer_thread = threading.Thread(target=observer.run)
        observer_thread.start()
        
        # start event listene
        event_manager = EventListener(wake_up=observer.wake_up)
        event_manager_thread = threading.Thread(target=event_manager.run)
        event_manager_thread.start()
        logger.log_exc("Exception in child thread")

