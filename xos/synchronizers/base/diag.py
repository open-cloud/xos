import os
import time
import sys
import traceback
import json

from core.models import Diag
from xos.config import Config, XOS_DIR
from xos.logger import Logger, logging, logger

logger = Logger(level=logging.INFO)

def update_diag(loop_end=None, loop_start=None, syncrecord_start=None, sync_start=None, backend_status=None):
    try:
        observer_name = Config().observer_name
    except:
        observer_name = 'openstack'

    try:
        diag = Diag.objects.filter(name=observer_name).first()
        if (not diag):
            diag = Diag(name=observer_name)
        br_str = diag.backend_register
        br = json.loads(br_str)
        if loop_end:
            br['last_run'] = loop_end
        if loop_end and loop_start:
            br['last_duration'] = loop_end - loop_start
        if syncrecord_start:
            br['last_syncrecord_start'] = syncrecord_start
        if sync_start:
            br['last_synchronizer_start'] = sync_start
        if backend_status:
            diag.backend_status = backend_status
        diag.backend_register = json.dumps(br)
        diag.save()
    except:
        logger.log_exc("Exception in update_diag")
        traceback.print_exc()

