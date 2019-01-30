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

from xosapi.orm import ORMWrapper, register_convenience_wrapper


class ORMWrapperController(ORMWrapper):
    @property
    def auth_url_v3(self):
        if self.auth_url and self.auth_url[-1] == "/":
            return "{}/v3/".format("/".join(self.auth_url.split("/")[:-2]))
        else:
            return "{}/v3/".format("/".join(self.auth_url.split("/")[:-1]))


register_convenience_wrapper("Controller", ORMWrapperController)
