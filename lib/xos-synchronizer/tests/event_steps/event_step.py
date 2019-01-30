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

from __future__ import print_function
from xossynchronizer.event_steps.eventstep import EventStep
from xossynchronizer.mock_modelaccessor import *


class TestEventStep(EventStep):
    technology = "kafka"
    topics = ["sometopic"]
    pattern = None

    def __init__(self, model_accessor, log, *args, **kwargs):
        super(TestEventStep, self).__init__(model_accessor, log, *args, **kwargs)

    def process_event(self, event):
        print("received an event", event)
