
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
import yaml
from protos import modeldefs_pb2
from google.protobuf.empty_pb2 import Empty

from xos.exceptions import *
from apihelper import XOSAPIHelperMixin

def yaml_to_grpc(yaml_repr, grpc_container, yaml_key = None, grpc_parent = None):
    if isinstance(yaml_repr, dict):
        for k,v in yaml_repr.items():
            grpc_sub_container = getattr(grpc_container, k)
            yaml_to_grpc(v, grpc_sub_container, k, grpc_container)
    elif isinstance(yaml_repr, list):
        for i in yaml_repr:
            grpc_sub_container = grpc_container.add()
            yaml_to_grpc(i, grpc_sub_container, None, grpc_container)
    else:
        setattr(grpc_parent, yaml_key, yaml_repr)

class ModelDefsService(modeldefs_pb2.modeldefsServicer, XOSAPIHelperMixin):
    def __init__(self, thread_pool):
        self.thread_pool = thread_pool

    def stop(self):
        pass

    def ListModelDefs(self, request, context):
        ystr = open('protos/modeldefs.yaml').read()
        yaml_repr = yaml.load(ystr)

        modeldefs = modeldefs_pb2.ModelDefs()

        yaml_to_grpc(yaml_repr, modeldefs)

        return modeldefs


if __name__=='__main__':
    ystr = open('protos/modeldefs.yaml').read()
    yaml_repr = yaml.load(ystr)

    modeldefs = modeldefs_pb2.ModelDefs()
    yaml_to_grpc(yaml_repr, modeldefs)
    print modeldefs
    
