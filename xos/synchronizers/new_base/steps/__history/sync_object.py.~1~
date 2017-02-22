import os
import base64
from collections import defaultdict
from django.db.models import F, Q
from xos.config import Config
from synchronizers.base.syncstep import *
from core.models import *
from synchronizers.base.ansible_helper import *
from xos.logger import observer_logger as logger
import json

class SyncObject(SyncStep):
    provides=[] # Caller fills this in
    requested_interval=0
    observes=[] # Caller fills this in

    def sync_record(self, r):
        raise DeferredException('Waiting for Service dependency: %r'%r)
