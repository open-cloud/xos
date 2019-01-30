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


""" policy.py

    Base Classes for Model Policies
"""

from __future__ import absolute_import

from multistructlog import create_logger
from xosconfig import Config

log = create_logger(Config().get("logging"))


class Policy(object):
    """ An XOS Model Policy

        Set the class member model_name to the name of the model that this policy will act on.

        The following functions will be invoked if they are defined:

            handle_create ... called when a model is created
            handle_update ... called when a model is updated
            handle_delete ... called when a model is deleted
    """

    def __init__(self, model_accessor):
        self.model_accessor = model_accessor
        self.logger = log
