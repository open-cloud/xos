import threading
import requests, json

from core.models import *
from planetstack.config import Config
from observer.deleters import deleters

import os
import base64
from fofum import Fofum
import json

# decorator that marks dispatachable event methods    
def event(func):
    setattr(func, 'event', func.__name__)
    return func         

class EventHandler:
    # This code is currently not in use.
    def __init__(self):
        pass 

    @staticmethod
    def get_events():
        events = []
        for name in dir(EventHandler):
            attribute = getattr(EventHandler, name)
            if hasattr(attribute, 'event'):
                events.append(getattr(attribute, 'event'))
        return events

    def dispatch(self, event, *args, **kwds):
        if hasattr(self, event):
            return getattr(self, event)(*args, **kwds)
            
        
class EventSender:
    def __init__(self,user=None,clientid=None):
        try:
            clid = Config().feefie_client_id
            user = Config().feefie_client_user
        except:
            clid = 'planetstack_core_team'
            user = 'pl'

        self.fofum = Fofum(user=user)
        self.fofum.make(clid)

    def fire(self,**args):
        self.fofum.fire(json.dumps(args))

class EventListener:
    def __init__(self,wake_up=None):
        self.handler = EventHandler()
        self.wake_up = wake_up

    def handle_event(self, payload):
        payload_dict = json.loads(payload)

        try:
            deletion = payload_dict['deletion_flag']
            if (deletion):
                model = payload_dict['model']
                pk = payload_dict['pk']

                for deleter in deleters[model]:
                    deleter(pk)
        except:
            deletion = False

        if (not deletion and self.wake_up):
            self.wake_up()
        

    def run(self):
        # This is our unique client id, to be used when firing and receiving events
        # It needs to be generated once and placed in the config file

        try:
            clid = Config().feefie_client_id
            user = Config().feefie_client_user
        except:
            clid = 'planetstack_core_team'
            user = 'pl'

        f = Fofum(user=user)
        
        listener_thread = threading.Thread(target=f.listen_for_event,args=(clid,self.handle_event))
        listener_thread.start()
