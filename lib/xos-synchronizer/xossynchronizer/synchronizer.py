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

from __future__ import absolute_import

import time

from multistructlog import create_logger
from xosconfig import Config


class Synchronizer(object):
    def __init__(self):
        self.log = create_logger(Config().get("logging"))

    def create_model_accessor(self):
        from .modelaccessor import model_accessor

        self.model_accessor = model_accessor

    def wait_for_ready(self):
        models_active = False
        wait = False
        while not models_active:
            try:
                # variable is unused
                _i = self.model_accessor.Site.objects.first()  # noqa: F841
                models_active = True
            except Exception as e:
                self.log.info("Exception", e=e)
                self.log.info("Waiting for data model to come up before starting...")
                time.sleep(10)
                wait = True

        if wait:
            time.sleep(
                60
            )  # Safety factor, seeing that we stumbled waiting for the data model to come up.

    def run(self):
        self.create_model_accessor()
        self.wait_for_ready()

        # Don't import backend until after the model accessor has been initialized. This is to support sync steps that
        # use `from xossynchronizer.modelaccessor import ...` and require the model accessor to be initialized before
        # their code can be imported.

        from .backend import Backend

        log_closure = self.log.bind(synchronizer_name=Config().get("name"))
        backend = Backend(log=log_closure, model_accessor=self.model_accessor)
        backend.run()
