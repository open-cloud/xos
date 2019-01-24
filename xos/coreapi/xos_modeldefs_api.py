
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

import yaml
from protos import modeldefs_pb2, modeldefs_pb2_grpc
import grpc
from xos.exceptions import *
from apihelper import XOSAPIHelperMixin
from apistats import REQUEST_COUNT, track_request_time
from xosconfig import Config

from multistructlog import create_logger

log = create_logger(Config().get('logging'))

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
        try:
            setattr(grpc_parent, yaml_key, yaml_repr)
        except Exception, e:
            # NOTE would be nice to get the parent,
            # for example given this data structure:
            # - hint: ''
            #   name: AdmControl
            #   default: "0"
            #   options:
            #   - {'id': 0, 'label': 'ALL'}
            #   - {'id': 1, 'label': 'Voice Only'}
            #   - {'id': 2, 'label': 'Data Only'}
            #
            # we'll get the error: Failed to set attribute id on element FieldOption has it value is 0 and has the wrong type <type 'int'>
            # while printing "name: AdmControl" would be much better
            log.exception("Failed to set attribute %s on element %s has it value is %s and has the wrong type %s" % (yaml_key, grpc_parent.__class__.__name__, yaml_repr, type(yaml_repr)))
            raise e

class ModelDefsService(modeldefs_pb2_grpc.modeldefsServicer, XOSAPIHelperMixin):
    def __init__(self, thread_pool):
        self.thread_pool = thread_pool

    def stop(self):
        pass

    @track_request_time("Modeldefs", "ListModelDefs")
    def ListModelDefs(self, request, context):
        ystr = open('protos/modeldefs.yaml').read()
        yaml_repr = yaml.load(ystr)

        modeldefs = modeldefs_pb2.ModelDefs()

        yaml_to_grpc(yaml_repr, modeldefs)

        REQUEST_COUNT.labels('xos-core', "Modeldefs", "ListModelDefs", grpc.StatusCode.OK).inc()
        return modeldefs


if __name__=='__main__':
    ystr = open('protos/modeldefs.yaml').read()

    yaml_repr = yaml.load(ystr)

    modeldefs = modeldefs_pb2.ModelDefs()
    yaml_to_grpc(yaml_repr, modeldefs)
    print modeldefs
