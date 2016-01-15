from basetest import *

import logging
import StringIO
import subprocess
import sys

from synchronizers.base.event_loop import XOSObserver
from synchronizers.model_policy import run_policy_once
from xos.config import set_override
from xos.logger import Logger, observer_logger

class BaseObserverToscaTest(BaseToscaTest):
    hide_observer_output = True

    def __init__(self):
        super(BaseObserverToscaTest, self).__init__()

    def get_usable_deployment(self):
        return "MyDeployment"

    def get_usable_controller(self):
        return "CloudLab"

    def ensure_observer_not_running(self):
        ps_output = subprocess.Popen("ps -elfy", shell=True, stdout=subprocess.PIPE).stdout.read()
        if "/opt/xos/xos-observer.py" in ps_output:
            print >> sys.stderr, "an observer is still running"
            print >> sys.stderr, "please stop it, for example 'supervisorctl stop observer'"
            sys.exit(-1)

    def log_to_memory(self):
        logStream = StringIO.StringIO()
        handler = logging.StreamHandler(stream=logStream)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

        loggername = Logger().loggername
        log = logging.getLogger(loggername)
        for hdlr in log.handlers[:]:
            log.removeHandler(hdlr)
        log.addHandler(handler)
        log.propagate = False

        log = observer_logger.logger
        for hdlr in log.handlers[:]:
            log.removeHandler(hdlr)
        log.addHandler(handler)
        log.propagate = False

        self.logStream = logStream

    def hide_output(self):
        set_override("observer_console_print", False)
        self.log_to_memory()
        sys.stdout = self.logStream
        sys.stderr = self.logStream

    def restore_output(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        if not self.hide_observer_output:
            print self.logStream.getvalue()

    def save_output(self, what, fn):
        file(fn,"w").write(self.logStream.getvalue())
        print >> sys.__stdout__,"   (%s log saved to %s)" % (what, fn)

    def run_model_policy(self, save_output=None):
        self.ensure_observer_not_running()

        self.hide_output()
        try:
            print ">>>>> run model_policies"
            run_policy_once()
            print ">>>>> done model_policies"
            if save_output:
                self.save_output("model_policy",save_output)
        finally:
            self.restore_output()

    def run_observer(self, save_output=None):
        self.ensure_observer_not_running()
        self.log_to_memory()

        self.hide_output()
        try:
            print ">>>>> run observer"
            observer = XOSObserver()
            observer.run_once()
            print ">>>>> done observer"
            if save_output:
                self.save_output("observer",save_output)
        finally:
            self.restore_output()

