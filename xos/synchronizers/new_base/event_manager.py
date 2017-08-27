
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

# FIXME Appear that a lot of unused code sits in here

import threading
from xosconfig import Config
import uuid
import os
import imp
import inspect
import base64
import json
import traceback

# NOTE can we use a path relative to this file?
XOS_DIR = "/opt/xos"

# NOTE I believe fofum is not used anymore, can we remove this?
if Config.get("fofum_disabled") is None:
    from fofum import Fofum
    fofum_enabled = True
else:
    fofum_enabled = False

random_client_id=None
def get_random_client_id():
    global random_client_id

    if (random_client_id is None) and os.path.exists(XOS_DIR + "/random_client_id"):
        # try to use the last one we used, if we saved it
        try:
            random_client_id = open(XOS_DIR+"/random_client_id","r").readline().strip()
            print "get_random_client_id: loaded %s" % random_client_id
        except:
            print "get_random_client_id: failed to read " + XOS_DIR + "/random_client_id"

    if random_client_id is None:
        random_client_id = base64.urlsafe_b64encode(os.urandom(12))
        print "get_random_client_id: generated new id %s" % random_client_id

        # try to save it for later (XXX: could race with another client here)
        try:
            open(XOS_DIR + "/random_client_id","w").write("%s\n" % random_client_id)
        except:
            print "get_random_client_id: failed to write " + XOS_DIR + "/random_client_id"

    return random_client_id

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

        user = Config.get("feefie.client_user")

        try:
            clid = Config.get("feefie.client_id")
        except:
            clid = get_random_client_id()
            print "EventSender: no feefie_client_id configured. Using random id %s" % clid

        if fofum_enabled:
            self.fofum = Fofum(user=user)
            self.fofum.make(clid)

    def fire(self,**kwargs):
        kwargs["uuid"] = str(uuid.uuid1())
        if fofum_enabled:
            self.fofum.fire(json.dumps(kwargs))

class EventListener:
    def __init__(self,wake_up=None):
        self.handler = EventHandler()
        self.wake_up = wake_up

    def handle_event(self, payload):
        payload_dict = json.loads(payload)

        if (self.wake_up):
            self.wake_up()

    def run(self):
        # This is our unique client id, to be used when firing and receiving events
        # It needs to be generated once and placed in the config file

        user = Config.get("feefie.client_user")

        try:
            clid = Config.get("feefie.client_id")
        except:
            clid = get_random_client_id()
            print "EventListener: no feefie_client_id configured. Using random id %s" % clid

        if fofum_enabled:
            f = Fofum(user=user)

            listener_thread = threading.Thread(target=f.listen_for_event,args=(clid,self.handle_event))
            listener_thread.start()
