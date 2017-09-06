
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


""" Reaper

    The reaper implements permanent deletion of soft-deleted objects.

    It does this by polling for soft-deleted objects. For each object, the
    reaper checks to see if its cascade set is empty. If so, the object will
    be purged. If it is non-empty, then the reaper will skip the object under
    the assumption that it will eventually become empty.
"""

import os
import sys
import threading

if __name__ == "__main__":
    import django
    sys.path.append('/opt/xos')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")

from datetime import datetime
from django.db import reset_queries
from django.db.models import F, Q
from django.db.models.signals import post_save
from django.db.transaction import atomic
from django.dispatch import receiver
from django.utils import timezone
from django.db import models as django_models
from core.models.xosbase import XOSCollector
from django.db import router

import pdb
import time
import traceback

from xosconfig import Config
from multistructlog import create_logger

log = create_logger(Config().get('logging'))

class ReaperThread(threading.Thread):
    daemon = True
    interval = 5

    def __init__(self, *args, **kwargs):
        self.terminate_signal = False
        super(ReaperThread, self).__init__(*args, **kwargs)

    def check_db_connection_okay(self):
        # django implodes if the database connection is closed by docker-compose
        from django import db
        try:
            db.connection.cursor()
            #diag = Diag.objects.filter(name="foo").first()
        except Exception, e:
            if "connection already closed" in traceback.format_exc():
               log.exception("XXX connection already closed", e = e)
               try:
    #               if db.connection:
    #                   db.connection.close()
                   db.close_old_connections()
               except Exception,e:
                    log.exception("XXX we failed to fix the failure", e = e)
            else:
               log.exception("XXX some other error", e = e)

    def journal_object(self, o, operation, msg=None, timestamp=None):
        # not implemented at this time
        pass

    def get_cascade_set(self, m):
        """ Get the set of objects that would cascade if this object was
            deleted.
        """
        collector = XOSCollector(using=router.db_for_write(m.__class__, instance=m))
        collector.collect([m])
        deps=[]
        for (k, models) in collector.data.items():
            for model in models:
                if model==m:
                    # collector will return ourself; ignore it.
                    continue
                if issubclass(m.__class__, model.__class__):
                    # collector will return our parent classes; ignore them.
                    continue
    # We don't actually need this check, as with multiple passes the reaper can
    # clean up a hierarchy of objects.
    #            if getattr(model, "backend_need_reap", False):
    #                # model is already marked for reaping; ignore it.
    #                continue
                deps.append(model)
        return deps

    def run_reaper_once(self):
            objects = []
            deleted_objects = []

            # logger.debug("REAPER: run_reaper_once()")

            self.check_db_connection_okay()

            # Reap non-sync'd models here
            # models_to_reap = [Slice,Network,NetworkSlice]

            models_to_reap = django_models.get_models(include_auto_created=False)
            for m in models_to_reap:
                if not hasattr(m, "deleted_objects"):
                    continue

                dobjs = m.deleted_objects.all()
                for d in dobjs:
                    if hasattr(d,"_meta") and hasattr(d._meta,"proxy") and d._meta.proxy:
                        # skip proxy objects; we'll get the base instead
                        continue

                    if (not getattr(d, "backend_need_reap", False)) and getattr(d, "backend_need_delete", False):
                        self.journal_object(d, "reaper.need_delete")
                        log.info("skipping because it has need_delete set", object = d)
                        continue

                    if (not getattr(d, "backend_need_reap", False)) and getattr(d, "backend_need_delete_policy", False):
                        log.info("skipping because it has need_delete_policy set", object = d)
                        continue

                    cascade_set = self.get_cascade_set(d)
                    if cascade_set:
                        self.journal_object(d, "reaper.cascade_set", msg=",".join([str(m) for m in cascade_set]))
                        log.info('REAPER: cannot purge object because its cascade_set is nonempty',object = d, cascade_set = ",".join([str(m) for m in cascade_set]))
                        continue

#                    XXX I don't think we need dependency_walker here anymore,
#                    XXX since the cascade set would include any inverse
#                    XXX dependencies automatically.
#                    deps = walk_inv_deps(noop, d)
#                    if (not deps):

                    if (True):
                        self.journal_object(d, "reaper.purge")
                        log.info('REAPER: purging object',object = d)
                        try:
                            d.delete(purge=True)
                        except:
                            self.journal_object(d, "reaper.purge.exception")
                            log.error('REAPER: exception purging object', object = d)
                            traceback.print_exc()
            try:
                reset_queries()
            except:
                # this shouldn't happen, but in case it does, catch it...
                log.exception("REAPER: exception in reset_queries")

            # logger.debug("REAPER: finished run_reaper_once()")

    def run(self):
        while (not self.terminate_signal):
            start = time.time()
            try:
                self.run_reaper_once()
            except:
                log.exception("REAPER: Exception in run loop")

            telap = time.time()-start
            if telap<self.interval:
                time.sleep(self.interval - telap)

    def stop(self):
        self.terminate_signal = True

if __name__ == '__main__':
    django.setup()

    reaper = ReaperThread()
    reaper.start()

    import time
    _ONE_DAY_IN_SECONDS = 60 * 60 * 24
    try:
        while 1:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        reaper.stop()

