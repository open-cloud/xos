
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


import base64
import time
from protos import xos_pb2
from google.protobuf.empty_pb2 import Empty

from django.contrib.auth import authenticate as django_authenticate
from xos.exceptions import *
from apihelper import XOSAPIHelperMixin, translate_exceptions

class XosService(xos_pb2.xosServicer, XOSAPIHelperMixin):
    def __init__(self, thread_pool):
        self.thread_pool = thread_pool
        XOSAPIHelperMixin.__init__(self)

    def stop(self):
        pass

{% for object in generator.all() %}
    @translate_exceptions
    def List{{ object.camel() }}(self, request, context):
      user=self.authenticate(context)
      model=self.get_model("{{ object.camel() }}")
      return self.querysetToProto(model, model.objects.all())

    @translate_exceptions
    def Filter{{ object.camel() }}(self, request, context):
      user=self.authenticate(context)
      model=self.get_model("{{ object.camel() }}")
      return self.filter(model, request)

    @translate_exceptions
    def Get{{ object.camel() }}(self, request, context):
      user=self.authenticate(context)
      model=self.get_model("{{ object.camel() }}")
      return self.get(model, request.id)

    @translate_exceptions
    def Create{{ object.camel() }}(self, request, context):
      user=self.authenticate(context)
      model=self.get_model("{{ object.camel() }}")
      return self.create(model, user, request)

    @translate_exceptions
    def Delete{{ object.camel() }}(self, request, context):
      user=self.authenticate(context)
      model=self.get_model("{{ object.camel() }}")
      return self.delete(model, user, request.id)

    @translate_exceptions
    def Update{{ object.camel() }}(self, request, context):
      user=self.authenticate(context)
      model=self.get_model("{{ object.camel() }}")
      return self.update(model, user, request.id, request, context)

{% endfor %}


