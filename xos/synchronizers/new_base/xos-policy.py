
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

import time
from synchronizers.new_base.model_policy_loop import XOSPolicyEngine
from synchronizers.new_base.modelaccessor import *

from xosconfig import Config
from multistructlog import create_logger

log = create_logger(Config().get('logging'))

def main():

    models_active = False
    wait = False
    while not models_active:
        try:
            _ = Instance.objects.first()
            _ = NetworkTemplate.objects.first()
            models_active = True
        except Exception,e:
            log.exception("Exception", e = e)
            log.info('Waiting for data model to come up before starting...')
            time.sleep(10)
            wait = True

    if (wait):
        time.sleep(60) # Safety factor, seeing that we stumbled waiting for the data model to come up.

    # start model policies thread
    policies_dir = Config.get("model_policies_dir")

    XOSPolicyEngine(policies_dir=policies_dir).run()

if __name__ == '__main__':
    main()
