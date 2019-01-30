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

from __future__ import absolute_import, print_function

import sys
import threading
import time

from multistructlog import create_logger
from xosconfig import Config

log = create_logger(Config().get("logging"))


class Backend:
    def run(self):
        # start model policies thread
        policies_dir = Config("model_policies_dir")
        if policies_dir:
            from synchronizers.model_policy import run_policy

            model_policy_thread = threading.Thread(target=run_policy)
            model_policy_thread.start()
        else:
            model_policy_thread = None
            log.info("Skipping model policies thread due to no model_policies dir.")

        while True:
            try:
                time.sleep(1000)
            except KeyboardInterrupt:
                print("exiting due to keyboard interrupt")
                if model_policy_thread:
                    model_policy_thread._Thread__stop()
                sys.exit(1)
