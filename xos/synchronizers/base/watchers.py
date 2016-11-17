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
from core.models import *
from django.db.models import F, Q
from django.db import connection
from django.db import reset_queries
from xos.logger import Logger, logging, logger
from xos.config import Config, XOS_DIR
from synchronizers.base.steps import *
from syncstep import SyncStep
from synchronizers.base.error_mapper import *
from synchronizers.base.steps.sync_object import SyncObject
from django.utils import timezone
from diag import update_diag
import redis

logger = Logger(level=logging.INFO)

class XOSWatcher:
    def load_sync_step_modules(self, step_dir=None):
        if step_dir is None:
            try:
                step_dir = Config().observer_steps_dir
            except:
                step_dir = '/opt/xos/synchronizers/openstack/steps'


        for fn in os.listdir(step_dir):
            pathname = os.path.join(step_dir,fn)
            if os.path.isfile(pathname) and fn.endswith(".py") and (fn!="__init__.py"):
                module = imp.load_source(fn[:-3],pathname)
                for classname in dir(module):
                    c = getattr(module, classname, None)

                    # make sure 'c' is a descendent of SyncStep and has a
                    # provides field (this eliminates the abstract base classes
                    # since they don't have a provides)

                    if inspect.isclass(c) and issubclass(c, SyncStep) and hasattr(c,"provides") and (c not in self.sync_steps):
                        self.sync_steps.append(c)

    def load_sync_steps(self):
        for s in self.sync_steps:
            if hasattr(s,'watches'):
                for w in s.watches:
                    w.source = s
                    try:
                        self.watch_map[w.dest.__name__].append(w)
                    except:
                        self.watch_map[w.dest.__name__]=[w]

    def __init__(self,sync_steps):
        self.watch_map = {}
        self.sync_steps = sync_steps
        #self.load_sync_step_modules()
        self.load_sync_steps()
        r = redis.Redis("redis")
        channels = self.watch_map.keys()
        self.redis = r
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(channels)
        logger.info("XOS watcher initialized")

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
                logger.warn("XOS watcher: exception %s while processing object: %s" % (type(e),e))
                pass
