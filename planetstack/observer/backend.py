import threading
import time
from observer.event_loop import PlanetStackObserver
from observer.event_manager import EventListener
from util.logger import Logger, logging

logger = Logger(level=logging.INFO)

class Backend:
    
    def run(self):
        try:
            # start the openstack observer
            observer = PlanetStackObserver()
            observer_thread = threading.Thread(target=observer.run)
            observer_thread.start()
            
            # start event listene
            event_manager = EventListener(wake_up=observer.wake_up)
            event_manager_thread = threading.Thread(target=event_manager.run)
            event_manager_thread.start()
        except:
            logger.log_exc("Exception in child thread")

