import threading
import requests, json
from core.models import *
from openstack.manager import OpenStackManager

import os
import base64
import fofum

# decorator that marks dispatachable event methods  
def event(func):
    setattr(func, 'event', func.__name__)
    return func      

class EventHandler:

    def __init__(self):
        self.manager = OpenStackManager()

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
            
        
    @event
    def save_site(self, id):
        sites = Site.objects.filter(id=id)
        if sites:
            self.manager.save_site(sites[0])
    
    @event
    def delete_site(self, tenant_id):
        self.manager.driver.delete_tenant(tenant_id)

    @event
    def save_site_privilege(self, id):
        site_privileges = SitePrivilege.objects.filter(id=id)
        if site_privileges:
            site_priv = self.manager.save_site_privilege(site_privileges[0])

    @event
    def delete_site_privilege(self, kuser_id, tenant_id, role_type):
        self.manager.driver.delete_user_role(kuser_id, tenant_id, role_type)

    @event
    def save_slice(self, id):
        slices = Slice.objects.filter(id=id)
        if slices:
            self.manager.save_slice(slices[0])
    
    @event
    def delete_slice(self, tenant_id, network_id, router_id, subnet_id):
        self.manager._delete_slice(tenant_id, network_id, router_id, subnet_id)

    @event
    def save_user(self, id):
        users = User.objects.filter(id=id)
        if users:
            self.manager.save_user(users[0])
        
    @event
    def delete_user(self, kuser_id):
        self.manager.driver.delete_user(kuser_id)
    
    @event
    def save_sliver(self, id):
        slivers = Sliver.objects.filter(id=id)
        if slivers:
            self.manager.save_sliver(slivers[0])

    @event
    def delete_sliver(self, instance_id):
        self.manager.destroy_instance(instance_id)                            

    

class EventListener:
    def __init__(self):
        self.handler = EventHandler()

    def handle_event(self, payload):
        payload_dict = json.loads(payload)
        event = payload_dict['event']
        ctx = payload_dict['ctx']
        self.handler.dispatch(event,**ctx)   

    def run(self):
        # This is our unique client id, to be used when firing and receiving events
        clid = base64.urlsafe_b64encode(os.urandom(12))

        f = Fofum()
        
        listener_thread = threading.Thread(target=f.listen_on_event,args=(clid,self.handle_event))
        listener_thread.start()
