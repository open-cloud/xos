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

from .config import Config

# Custom TRACE logging level
# ref: https://stackoverflow.com/questions/2183233/how-to-add-a-custom-loglevel-to-pythons-logging-facility/13638084#13638084

import logging

# Logging levels: https://docs.python.org/2/library/logging.html#logging-levels
# Add a sub-DEBUG Trace level
TRACE_LOGLVL = 5

logging.addLevelName(TRACE_LOGLVL, "TRACE")


def trace_loglevel(self, message, *args, **kws):
    if self.isEnabledFor(TRACE_LOGLVL):
        self._log(TRACE_LOGLVL, message, args, **kws)


logging.Logger.trace = trace_loglevel
