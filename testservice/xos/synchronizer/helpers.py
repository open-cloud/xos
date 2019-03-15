# Copyright 2018-present Open Networking Foundation
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

from __future__ import absolute_import

import os
import time


def get_signal_fn(model, name):
    return os.path.join("/tmp", "signal_%s_%s_%s" % (model.model_name, model.id, name))


def put_signal(log, model, name):
    open(get_signal_fn(model, name), "a").write(str(time.time()) + "\n")


def wait_for_signal(log, model, name, timeout=30):
    fn = get_signal_fn(model, name)
    count = 0
    while not os.path.exists(fn):
        count += 1
        if (count > 30):
            log.error("TEST:FAIL - Timeout waiting for %s" % fn, model=model)
            raise Exception("timeout")
        time.sleep(1)
