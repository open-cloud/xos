import threading
from openstack.sliveragent import SliverAgent
from openstack.observer import OpenStackObserver
from openstack.event_listener import EventListener

class Backend:
    
    def run(self):
        # start the openstack observer
        observer = OpenStackObserver()
        observer_thread = threading.Thread(target=observer.run)
        observer_thread.start()

        # start event listene
        event_listener = EventListener()
        event_listener_thread = threading.Thread(target=event_listener.run)
        event_listener_thread.start()
                
