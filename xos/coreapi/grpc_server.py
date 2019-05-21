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

"""gRPC server endpoint"""
import os
import sys
import threading
from collections import OrderedDict
from os.path import abspath, basename, dirname, join
import grpc
from grpc_reflection.v1alpha import reflection
from concurrent import futures
import zlib
from protos import schema_pb2, schema_pb2_grpc

# initialize config and logger
from xosconfig import Config
from multistructlog import create_logger

xos_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + "/..")
sys.path.append(xos_path)

Config.init()
log = create_logger(Config().get("logging"))

SERVER_KEY = "/opt/cord_profile/core_api_key.pem"
SERVER_CERT = "/opt/cord_profile/core_api_cert.pem"
SERVER_CA = "/usr/local/share/ca-certificates/local_certs.crt"


class SchemaService(schema_pb2_grpc.SchemaServiceServicer):
    def __init__(self, thread_pool):
        self.thread_pool = thread_pool
        protos = self._load_schema()
        self.schemas = schema_pb2.Schemas(
            protos=protos, swagger_from="xos.proto", yang_from="xos.proto"
        )

    def stop(self):
        pass

    def _load_schema(self):
        """Pre-load schema file so that we can serve it up (file sizes
           are small enough to do so
        """
        proto_dir = abspath(join(dirname(__file__), "./protos"))

        def find_files(dir, suffix):
            proto_blacklist = ["schema.proto"]

            proto_files = [
                join(dir, fname)
                for fname in os.listdir(dir)
                if fname.endswith(suffix) and fname not in proto_blacklist
            ]
            return proto_files

        proto_map = OrderedDict()  # to have deterministic data
        for proto_file in find_files(proto_dir, ".proto"):
            with open(proto_file, "r") as f:
                proto_content = f.read()
            fname = basename(proto_file)
            # assure no two files have the same basename
            assert fname not in proto_map

            desc_file = proto_file.replace(".proto", ".desc")
            with open(desc_file, "r") as f:
                descriptor_content = zlib.compress(f.read())

            proto_map[fname] = schema_pb2.ProtoFile(
                file_name=fname, proto=proto_content, descriptor=descriptor_content
            )

        return proto_map.values()

    def GetSchema(self, request, context):
        """Return current schema files and descriptor"""
        return self.schemas


class XOSGrpcServer(object):
    def __init__(self, port=50055, model_status=0, model_output=""):
        self.port = port
        self.model_status = model_status
        self.model_output = model_output
        log.info("Initializing GRPC Server", port=port)
        self.thread_pool = futures.ThreadPoolExecutor(max_workers=10)
        self.server = grpc.server(self.thread_pool)
        self.django_initialized = False
        self.django_apps = []

        server_key = open(SERVER_KEY, "r").read()
        server_cert = open(SERVER_CERT, "r").read()
        server_ca = open(SERVER_CA, "r").read()

        self.credentials = grpc.ssl_server_credentials(
            [(server_key, server_cert)], server_ca, False
        )

        self.delayed_shutdown_timer = None
        self.exit_event = threading.Event()

        self.services = []

    def init_django(self):
        try:
            import django

            os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")
            django.setup()
            from django.apps import apps

            self.django_apps = apps
            self.django_initialized = True
        except BaseException:
            log.exception("Failed to initialize django")

    def register_dynamicload(self):
        from xos_dynamicload_api import DynamicLoadService
        from protos import dynamicload_pb2_grpc, dynamicload_pb2

        dynamic_load_service = DynamicLoadService(self.thread_pool, self)
        self.register(
            "dynamicload",
            dynamicload_pb2_grpc.add_dynamicloadServicer_to_server,
            dynamic_load_service,
        )
        dynamic_load_service.set_django_apps(self.django_apps)

        self.service_names.append(dynamicload_pb2.DESCRIPTOR.services_by_name['dynamicload'].full_name)

    def register_core(self):
        from xos_grpc_api import XosService
        from protos import xos_pb2_grpc, xos_pb2

        self.register(
            "xos", xos_pb2_grpc.add_xosServicer_to_server, XosService(self.thread_pool)
        )

        self.service_names.append(xos_pb2.DESCRIPTOR.services_by_name['xos'].full_name)

    def register_utility(self):
        from xos_utility_api import UtilityService
        from protos import utility_pb2_grpc, utility_pb2

        self.register(
            "utility",
            utility_pb2_grpc.add_utilityServicer_to_server,
            UtilityService(self.thread_pool),
        )

        self.service_names.append(utility_pb2.DESCRIPTOR.services_by_name['utility'].full_name)

    def register_modeldefs(self):
        from xos_modeldefs_api import ModelDefsService
        from protos import modeldefs_pb2_grpc, modeldefs_pb2

        self.register(
            "modeldefs",
            modeldefs_pb2_grpc.add_modeldefsServicer_to_server,
            ModelDefsService(self.thread_pool),
        )

        self.service_names.append(modeldefs_pb2.DESCRIPTOR.services_by_name['modeldefs'].full_name)

    def register_filetransfer(self):
        from xos_filetransfer_api import FileTransferService
        from protos import filetransfer_pb2_grpc, filetransfer_pb2

        self.register(
            "filetransfer",
            filetransfer_pb2_grpc.add_filetransferServicer_to_server,
            FileTransferService(self.thread_pool),
        )

        self.service_names.append(filetransfer_pb2.DESCRIPTOR.services_by_name['filetransfer'].full_name)

    def start(self):
        log.info("Starting GRPC Server")

        self.service_names = []

        self.register(
            "schema",
            schema_pb2_grpc.add_SchemaServiceServicer_to_server,
            SchemaService(self.thread_pool),
        )

        if self.model_status != 0:
            log.error("Models are broken. Please remove the synchronizer causing the problem and restart the core.")
            sys.exit(-1)

        self.init_django()

        if not self.django_initialized:
            log.error("Django is broken. Please remove the synchronizer causing the problem and restart the core.")
            sys.exit(-1)

        self.register_dynamicload()
        self.register_core()
        self.register_utility()
        self.register_modeldefs()
        self.register_filetransfer()

        self.service_names.append(reflection.SERVICE_NAME)
        reflection.enable_server_reflection(self.service_names, self.server)

        # open port
        self.server.add_insecure_port("[::]:%s" % self.port)

        self.server.add_secure_port("[::]:50051", self.credentials)

        # strat the server
        self.server.start()

        log.info("GRPC Server Started")
        return self

    def stop(self, grace=0):
        log.info("Stopping GRPC Server")
        for service in self.services:
            service.stop()
        self.server.stop(grace)
        log.info("stopped")

    def stop_and_exit(self):
        log.info("Stop and Exit")
        self.exit_event.set()

    def register(self, name, activator_func, service):
        """
        Allow late registration of gRPC servicers
        :param activator_func: The gRPC "add_XYZServicer_to_server method
        autogenerated by protoc.
        :param service: The object implementing the service.
        :return: None
        """
        self.services.append(service)
        activator_func(service, self.server)

    def delayed_shutdown(self, seconds):
        log.info("Delayed shutdown", seconds=seconds)
        if self.delayed_shutdown_timer:
            self.delayed_shutdown_timer.cancel()
        self.delayed_shutdown_timer = threading.Timer(seconds, self.stop_and_exit)
        self.delayed_shutdown_timer.start()
