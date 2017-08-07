
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


""" A very simple Tosca daemon. Every ten seconds it looks for new programs in
    "run" or "destroy" status, and executes them.

    TODO: Replace this with observer and/or model_policies ?
"""

import os
import sys
from threading import Thread
import time

# add the parent directory to sys.path
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")
import django
django.setup()

from core.models import Program, User
from nodeselect import XOSNodeSelector
from imageselect import XOSImageSelector
import traceback

from engine import XOSTosca

class ToscaDaemon(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True

    def run_program(self, model):
        try:
            print "*** Run Program %s ***" % model.name
            model.status = "executing"
            model.messages = ""
            model.save()
            xt = XOSTosca(model.contents, parent_dir=currentdir, log_to_console=True)
            xt.execute(model.owner)
            model.messages = "\n".join(xt.log_msgs)
            model.status = "complete"
        except:
            model.messages = traceback.format_exc()
            model.status = "exception"
            traceback.print_exc()
        model.command = None
        model.save()

    def destroy_program(self, model):
        try:
            print "*** Destroy Program %s ***" % model.name
            model.status = "executing"
            model.messages = ""
            model.save()
            xt = XOSTosca(model.contents, parent_dir=currentdir)
            xt.destroy(model.owner)
            model.messages = "\n".join(xt.log_msgs)
            model.status = "complete"
        except:
            model.messages = traceback.format_exc()
            model.status = "exception"
            traceback.print_exc()
        model.command = None
        model.save()

    def run_once(self):
        models = Program.objects.filter(kind="tosca", command="run")
        for model in models:
            self.run_program(model)

        models = Program.objects.filter(kind="tosca", command="destroy")
        for model in models:
            self.destroy_program(model)

    def run(self):
        while True:
            self.run_once()
            time.sleep(10)
            django.db.reset_queries()

if __name__ == "__main__":
    if "--once" in sys.argv:
        ToscaDaemon().execute_once()
    else:
        ToscaDaemon().start()

        print "Running forever..."
        while True:
            time.sleep(60)

