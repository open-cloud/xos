
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


#
# Copyright 2017 the original author or authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""gRPC server endpoint"""
import os
import sys
import uuid
from collections import OrderedDict
from os.path import abspath, basename, dirname, join, walk
import grpc
from concurrent import futures
import zlib

from xosconfig import Config

from multistructlog import create_logger

log = create_logger(Config().get('logging'))

if __name__ == "__main__":
    import django
    sys.path.append('/opt/xos')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")

from protos import xos_pb2, schema_pb2, modeldefs_pb2, utility_pb2
from xos_grpc_api import XosService
from xos_modeldefs_api import ModelDefsService
from xos_utility_api import UtilityService
from google.protobuf.empty_pb2 import Empty



SERVER_KEY="/opt/cord_profile/core_api_key.pem"
SERVER_CERT="/opt/cord_profile/core_api_cert.pem"
SERVER_CA="/usr/local/share/ca-certificates/local_certs.crt"

#SERVER_KEY="certs/server.key"
#SERVER_CERT="certs/server.crt"
#SERVER_CA="certs/ca.crt"

class SchemaService(schema_pb2.SchemaServiceServicer):

    def __init__(self, thread_pool):
        self.thread_pool = thread_pool
        protos = self._load_schema()
        self.schemas = schema_pb2.Schemas(protos=protos,
                                          swagger_from='xos.proto',
                                          yang_from='xos.proto')

    def stop(self):
        pass

    def _load_schema(self):
        """Pre-load schema file so that we can serve it up (file sizes
           are small enough to do so
        """
        proto_dir = abspath(join(dirname(__file__), './protos'))

        def find_files(dir, suffix):
            proto_files = [
                join(dir, fname) for fname in os.listdir(dir)
                if fname.endswith(suffix)
            ]
            return proto_files

        proto_map = OrderedDict()  # to have deterministic data
        for proto_file in find_files(proto_dir, '.proto'):
            with open(proto_file, 'r') as f:
                proto_content = f.read()
            fname = basename(proto_file)
            # assure no two files have the same basename
            assert fname not in proto_map

            desc_file = proto_file.replace('.proto', '.desc')
            with open(desc_file, 'r') as f:
                descriptor_content = zlib.compress(f.read())

            proto_map[fname] = schema_pb2.ProtoFile(
                file_name=fname,
                proto=proto_content,
                descriptor=descriptor_content
            )

        return proto_map.values()

    def GetSchema(self, request, context):
        """Return current schema files and descriptor"""
        return self.schemas

class XOSGrpcServer(object):

    def __init__(self, port=50055):
        self.port = port
        log.info('Initializing GRPC Server', port = port)
        self.thread_pool = futures.ThreadPoolExecutor(max_workers=1)
        self.server = grpc.server(self.thread_pool)

        server_key = open(SERVER_KEY,"r").read()
        server_cert = open(SERVER_CERT,"r").read()
        server_ca = open(SERVER_CA,"r").read()

        self.credentials = grpc.ssl_server_credentials([(server_key, server_cert)], server_ca, False)

        self.services = []

    def start(self):
        log.info('Starting GRPC Server')

        # add each service unit to the server and also to the list
        for activator_func, service_class in (
            (schema_pb2.add_SchemaServiceServicer_to_server, SchemaService),
            (xos_pb2.add_xosServicer_to_server, XosService),
            (modeldefs_pb2.add_modeldefsServicer_to_server, ModelDefsService),
            (utility_pb2.add_utilityServicer_to_server, UtilityService),
        ):
            service = service_class(self.thread_pool)
            self.register(activator_func, service)

        # open port
        self.server.add_insecure_port('[::]:%s' % self.port)

        self.server.add_secure_port("[::]:50051", self.credentials)

        # strat the server
        self.server.start()

        log.info('GRPC Server Started')
        return self

    def stop(self, grace=0):
        log.info('Stopping GRPC Server')
        for service in self.services:
            service.stop()
        self.server.stop(grace)
        log.info('stopped')

    def register(self, activator_func, service):
        """
        Allow late registration of gRPC servicers
        :param activator_func: The gRPC "add_XYZServicer_to_server method
        autogenerated by protoc.
        :param service: The object implementing the service.
        :return: None
        """
        self.services.append(service)
        activator_func(service, self.server)


def restart_chameleon():
    import docker

    def find_container(client, search_name):
        for c in client.containers():
            for c_name in c["Names"]:
                if (search_name in c_name):
                    return c
        return None

    client=docker.from_env()
    chameleon_container = find_container(client, "xos_chameleon_1")
    if chameleon_container:
        try:
            # the first attempt always fails with 404 error
            # docker-py bug?
            client.restart(chameleon_container["Names"][0])
        except:
            client.restart(chameleon_container["Names"][0])


# This is to allow running the GRPC server in stand-alone mode

if __name__ == '__main__':
    django.setup()

    server = XOSGrpcServer().start()

    restart_chameleon()

    import time
    _ONE_DAY_IN_SECONDS = 60 * 60 * 24
    try:
        while 1:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop()


