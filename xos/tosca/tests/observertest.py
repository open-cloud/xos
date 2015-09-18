from basetest import *

import logging
import StringIO
import subprocess
import sys

from observer.event_loop import XOSObserver
from model_policy import run_policy_once
from xos.config import set_override
from util.logger import Logger, observer_logger

class BaseObserverToscaTest(BaseToscaTest):
    hide_observer_output = True

    def __init__(self):
        super(BaseObserverToscaTest, self).__init__()

    def ensure_observer_not_running(self):
        ps_output = subprocess.Popen("ps -elfy", shell=True, stdout=subprocess.PIPE).stdout.read()
        if "/opt/xos/xos-observer.py" in ps_output:
            print >> sys.stderr, "an observer is still running"
            print >> sys.stderr, "please stop it, for example 'supervisorctl stop observer'"
            sys.exit(-1)

    def log_to_memory(self):
        set_override("observer_console_print", False)

        if self.hide_observer_output:
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

    def run_model_policy(self):
        self.ensure_observer_not_running()
        self.log_to_memory()

        #print ">>>>> run model_policies"
        run_policy_once()
        #print ">>>>> done model_policies"

    def run_observer(self):
        self.ensure_observer_not_running()
        self.log_to_memory()

        observer = XOSObserver()
        #print ">>>>> run observer"
        observer.run_once()
        #print ">>>>> done observer"

