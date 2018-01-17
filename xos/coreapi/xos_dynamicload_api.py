
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
import fnmatch
import os
import sys
import time
import traceback
from protos import dynamicload_pb2
from google.protobuf.empty_pb2 import Empty

from importlib import import_module

from dynamicbuild import DynamicBuilder

class DynamicLoadService(dynamicload_pb2.dynamicloadServicer):
    def __init__(self, thread_pool, server):
        self.thread_pool = thread_pool
        self.server = server

    def stop(self):
        pass

    def LoadModels(self, request, context):
        try:
            builder = DynamicBuilder()
            result = builder.handle_loadmodels_request(request)

            if (result == builder.SOMETHING_CHANGED):
                self.server.delayed_shutdown(5)

            response = dynamicload_pb2.LoadModelsReply()
            response.status = response.SUCCESS

            return response
        except Exception, e:
            import traceback; traceback.print_exc()
            raise e

    def UnloadModels(self, request, context):
        try:
            builder = DynamicBuilder()
            result = builder.handle_unloadmodels_request(request)

            if (result == builder.SOMETHING_CHANGED):
                self.server.delayed_shutdown(5)

            response = dynamicload_pb2.LoadModelsReply()
            response.status = response.SUCCESS

            return response
        except Exception, e:
            import traceback; traceback.print_exc()
            raise e

    def GetLoadStatus(self, request, context):
        try:
            builder = DynamicBuilder()
            manifests = builder.get_manifests()

            response = dynamicload_pb2.LoadStatusReply()
            response.model_status = self.server.model_status
            response.model_output = self.server.model_output
            for manifest in manifests:
                item = response.services.add()
                item.name = manifest["name"]
                item.version = manifest["version"]
                item.state = manifest.get("state", "unspecified")

            return response
        except Exception, e:
            import traceback; traceback.print_exc()
            raise e


