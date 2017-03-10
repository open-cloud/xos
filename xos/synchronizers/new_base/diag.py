import os
import time
import sys
import traceback
import json

from xos.config import Config, XOS_DIR
from xos.logger import Logger, logging, logger

logger = Logger(level=logging.INFO)

def update_diag(diag_class, loop_end=None, loop_start=None, syncrecord_start=None, sync_start=None, backend_status=None):
    observer_name = Config().observer_name

    try:
        diag = diag_class.objects.filter(name=observer_name).first()
        if (not diag):
            if hasattr(diag_class.objects, "new"):
                # api style
                diag = diag_class.objects.new(name=observer_name)
            else:
                # django style
                diag = diag_class(name=observer_name)
        br_str = diag.backend_register
        if br_str:
            br = json.loads(br_str)
        else:
            br = {}
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

