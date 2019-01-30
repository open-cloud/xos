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


class PullStep(object):
    """
    All the pull steps defined in each synchronizer needs to inherit from this class in order to be loaded
    """

    def __init__(self, **kwargs):
        """
        Initialize a pull step
        :param kwargs:
        -- observed_model: name of the model that is being polled
        -- model_accessor: used to create and update models
        """
        self.observed_model = kwargs.get("observed_model")
        self.model_accessor = kwargs.get("model_accessor")

    def pull_records(self):
        self.log.debug(
            "There is no default pull_records, please provide a pull_records method for %s"
            % self.observed_model
        )
