
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


import os
import inspect
import imp
import time
import sys
import traceback
import commands
import threading
import json
import pprint
import traceback

from datetime import datetime
from collections import defaultdict

from syncstep import SyncStep
from synchronizers.new_base.error_mapper import *
import redis

from xosconfig import Config
from multistructlog import create_logger

log = create_logger(Config().get('logging'))

class XOSWatcher:
    def load_sync_step_modules(self, step_dir=None):
        if step_dir is None:
            step_dir = Config.get("steps_dir")

        for fn in os.listdir(step_dir):
            pathname = os.path.join(step_dir, fn)
            if os.path.isfile(pathname) and fn.endswith(".py") and (fn != "__init__.py"):
                module = imp.load_source(fn[:-3], pathname)
                for classname in dir(module):
                    c = getattr(module, classname, None)

                    # make sure 'c' is a descendent of SyncStep and has a
                    # provides field (this eliminates the abstract base classes
                    # since they don't have a provides)

                    if inspect.isclass(c) and issubclass(c, SyncStep) and hasattr(c, "provides") and (
                        c not in self.sync_steps):
                        self.sync_steps.append(c)

    def load_sync_steps(self):
        for s in self.sync_steps:
            if hasattr(s, 'watches'):
                for w in s.watches:
                    w.source = s
                    try:
                        self.watch_map[w.dest.__name__].append(w)
                    except:
                        self.watch_map[w.dest.__name__] = [w]

    def __init__(self, sync_steps):
        self.watch_map = {}
        self.sync_steps = sync_steps
        # self.load_sync_step_modules()
        self.load_sync_steps()
        r = redis.Redis("redis")
        channels = self.watch_map.keys()
        self.redis = r
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(channels)
        log.info("XOS watcher initialized")

    def run(self):
        for item in self.pubsub.listen():
            channel = item['channel']
            try:
                entry = self.watch_map[channel]
                data = json.loads(item['data'])
                pk = data['pk']
                changed_fields = data['changed_fields']
                for w in entry:
                    if w.into in changed_fields or not w.into:
                        if (hasattr(w.source, 'handle_watched_object')):
                            o = w.dest.objects.get(pk=data['pk'])
                            step = w.source()
                            step.handle_watched_object(o)
            except Exception as e:
                log.exception("XOS watcher: exception while processing object", e = e)
                pass
