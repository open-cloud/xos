
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

import logging
import os

from nose2.events import Plugin

log = logging.getLogger('nose2.plugins.excludeignoredfiles')

class ExcludeIgnoredFiles(Plugin):
    commandLineSwitch = (None, 'exclude-ignored-files', 'Exclude that which should be excluded')

    def matchPath(self, event):
        if event.path.endswith(".py"):
            text = open(event.path, "r").read()
            if "test_framework: ignore" in text.lower():
                log.info("Ignoring %s" % event.path)
                event.handled = True
                return False
