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


class EventStep(object):
    """
    All the event steps defined in each synchronizer needs to inherit from this class in order to be loaded

    Each step should define a technology, and either a `topics` or a `pattern`. The meaning of `topics` and `pattern`
    depend on the technology that is chosen.
    """

    technology = "kafka"
    topics = []
    pattern = None

    def __init__(self, model_accessor, log, **kwargs):
        """
        Initialize a pull step. Override this function to include any initialization. Make sure to call the original
        __init__() from your method.
        """

        # self.model_accessor can be used to create and query models
        self.model_accessor = model_accessor

        # self.log can be used to emit logging messages.
        self.log = log

    def process_event(self, event):
        # This method must be overridden in your class. Do not call the original method.

        self.log.warning(
            "There is no default process_event, please provide a process_event method",
            msg=event,
        )
