#!/usr/bin/env python

""" xos-policy.py

    Standalone interface to model_policy engine.

    Normally model policies are run by the synchronizer. This file allows them to be run independently as an aid
    to development.
"""

import os
import sys

sys.path.append('/opt/xos')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")
from xosconfig import Config
from xos.logger import Logger, logging, logger
import time
from synchronizers.new_base.model_policy_loop import XOSPolicyEngine
from synchronizers.new_base.modelaccessor import *

logger = Logger(level=logging.INFO)

def main():

    models_active = False
    wait = False
    while not models_active:
        try:
            _ = Instance.objects.first()
            _ = NetworkTemplate.objects.first()
            models_active = True
        except Exception,e:
            logger.info(str(e))
            logger.info('Waiting for data model to come up before starting...')
            time.sleep(10)
            wait = True

    if (wait):
        time.sleep(60) # Safety factor, seeing that we stumbled waiting for the data model to come up.

    # start model policies thread
    policies_dir = Config.get("model_policies_dir")

    XOSPolicyEngine(policies_dir=policies_dir).run()

if __name__ == '__main__':
    main()
