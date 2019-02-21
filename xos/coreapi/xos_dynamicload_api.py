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

from protos import dynamicload_pb2
from protos import dynamicload_pb2_grpc

from xosutil.autodiscover_version import autodiscover_version_of_main
from dynamicbuild import DynamicBuilder
from apistats import REQUEST_COUNT, track_request_time
import grpc
import semver
import re
from xosconfig import Config
from multistructlog import create_logger

log = create_logger(Config().get("logging"))

class DynamicLoadService(dynamicload_pb2_grpc.dynamicloadServicer):
    def __init__(self, thread_pool, server):
        self.thread_pool = thread_pool
        self.server = server
        self.django_apps = None
        self.django_apps_by_name = {}

    def stop(self):
        pass

    def set_django_apps(self, django_apps):
        """ Allows the creator of DynamicLoadService to pass in a pointer to django's app list once django has been
            installed. This is optional. We don't import django.apps directly, as DynamicLoadService must be able
            to run even if django is broken due to modeling issues.
        """
        self.django_apps = django_apps

        # Build up some dictionaries used by the API handlers. We can build these once at initialization time because
        # when apps are onboarded, the core is always restarted.

        self.django_apps_by_name = {}
        self.django_app_models = {}
        if self.django_apps:
            for app in self.django_apps.get_app_configs():
                self.django_apps_by_name[app.name] = app

                # Build up a dictionary of all non-decl models.
                django_models = {}
                for (k, v) in app.models.items():
                    if not k.endswith("_decl"):
                        django_models[k] = v
                self.django_app_models[app.name] = django_models

    def match_major_version(self, current, expected):
        """
        Returns true if the major version is the same
        :param current: semver string for the current version
        :param expected: semver string for the expected version
        :return: bool
        """
        current_parts = semver.parse(current)
        expected = re.sub("[><=!]", "", expected)
        expected_parts = semver.parse(expected)
        match = current_parts["major"] == expected_parts["major"]
        log.debug("Verifying major version",
                  expected_major=expected_parts["major"], current_major=current_parts["major"], match=match)
        return match

    @track_request_time("DynamicLoad", "LoadModels")
    def LoadModels(self, request, context):
        try:

            core_version = autodiscover_version_of_main()
            requested_core_version = request.core_version
            log.info("Loading service models",
                     service=request.name,
                     service_version=request.version,
                     requested_core_version=requested_core_version
                )

            if not requested_core_version:
                requested_core_version = "<3.0.0"

            match_version = semver.match(core_version, requested_core_version)
            match_major = self.match_major_version(core_version, requested_core_version)
            if not match_version:
                log.error("Not loading service because of mismatching versions", service=request.name,
                          core_version=core_version, requested_core_version=requested_core_version)
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                msg = "Service %s is requesting core version %s but actual version is %s" % (
                request.name, requested_core_version, core_version)
                context.set_details(msg)
                raise Exception(msg)
            if not match_major:
                log.error("Not loading service because of mismatching major versions", service=request.name,
                          core_version=core_version, requested_core_version=requested_core_version)
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                msg = "Service %s is requesting core version %s but actual version is %s, major version is different" % (
                    request.name, requested_core_version, core_version)
                context.set_details(msg)
                raise Exception(msg)
                context.set_details(msg)
                raise Exception(msg)

            builder = DynamicBuilder()
            result = builder.handle_loadmodels_request(request)

            if result == builder.SUCCESS:
                self.server.delayed_shutdown(5)

            response = dynamicload_pb2.LoadModelsReply()
            response.status = result
            REQUEST_COUNT.labels(
                "xos-core", "DynamicLoad", "LoadModels", grpc.StatusCode.OK
            ).inc()
            return response
        except Exception as e:
            import traceback

            traceback.print_exc()
            REQUEST_COUNT.labels(
                "xos-core", "DynamicLoad", "LoadModels", grpc.StatusCode.INTERNAL
            ).inc()
            raise e

    def map_error_code(self, status, context):
        """ Map the DynamicLoad status into an appropriate gRPC status code
            and include an error description if appropriate.

            Chameleon supports limited mapping to http status codes.
            Picked a best-fit:
                OK = 200
                INVALID_ARGUMENT = 400
                ALREADY_EXISTS = 409
        """

        code_names = {
            DynamicBuilder.SUCCESS: "SUCCESS",
            DynamicBuilder.SUCCESS_NOTHING_CHANGED: "SUCCESS_NOTHING_CHANGED",
            DynamicBuilder.ERROR: "ERROR",
            DynamicBuilder.ERROR_LIVE_MODELS: "ERROR_LIVE_MODELS",
            DynamicBuilder.ERROR_DELETION_IN_PROGRESS: "ERROR_DELETION_IN_PROGRESS",
            DynamicBuilder.TRYAGAIN: "TRYAGAIN"}

        code_map = {
            DynamicBuilder.SUCCESS: grpc.StatusCode.OK,
            DynamicBuilder.SUCCESS_NOTHING_CHANGED: grpc.StatusCode.OK,
            DynamicBuilder.ERROR: grpc.StatusCode.INVALID_ARGUMENT,
            DynamicBuilder.ERROR_LIVE_MODELS: grpc.StatusCode.ALREADY_EXISTS,
            DynamicBuilder.ERROR_DELETION_IN_PROGRESS: grpc.StatusCode.ALREADY_EXISTS,
            DynamicBuilder.TRYAGAIN: grpc.StatusCode.OK}

        code = code_map.get(status, DynamicBuilder.ERROR)

        context.set_code(code)
        if code != grpc.StatusCode.OK:
            # In case of error, send helpful text back to the caller
            context.set_details(code_names.get(status, "UNKNOWN"))

    @track_request_time("DynamicLoad", "UnloadModels")
    def UnloadModels(self, request, context):
        try:
            builder = DynamicBuilder()
            result = builder.handle_unloadmodels_request(request,
                                                         self.django_app_models.get("services." + request.name, {}))

            if result == builder.SUCCESS:
                self.server.delayed_shutdown(5)

            self.map_error_code(result, context)

            response = dynamicload_pb2.LoadModelsReply()
            response.status = result
            REQUEST_COUNT.labels(
                "xos-core", "DynamicLoad", "UnloadModels", grpc.StatusCode.OK
            ).inc()
            return response
        except Exception as e:
            import traceback

            traceback.print_exc()
            REQUEST_COUNT.labels(
                "xos-core", "DynamicLoad", "UnloadModels", grpc.StatusCode.INTERNAL
            ).inc()
            raise e

    @track_request_time("DynamicLoad", "GetLoadStatus")
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

                if item.state == "load":
                    django_app = self.django_apps_by_name.get("services." + item.name)
                    if django_app:
                        item.state = "present"
                        # TODO: Might be useful to return a list of models as well

            # the core is always onboarded, so doesn't have an explicit manifest
            item = response.services.add()
            item.name = "core"
            item.version = autodiscover_version_of_main()
            if "core" in self.django_apps_by_name:
                item.state = "present"
            else:
                item.state = "load"
            REQUEST_COUNT.labels(
                "xos-core", "DynamicLoad", "GetLoadStatus", grpc.StatusCode.OK
            ).inc()
            return response
        except Exception as e:
            import traceback

            traceback.print_exc()
            REQUEST_COUNT.labels(
                "xos-core", "DynamicLoad", "GetLoadStatus", grpc.StatusCode.INTERNAL
            ).inc()
            raise e

    @track_request_time("DynamicLoad", "GetConvenienceMethods")
    def GetConvenienceMethods(self, request, context):
        # self.authenticate(context, required=True)
        try:
            builder = DynamicBuilder()
            manifests = builder.get_manifests()

            response = dynamicload_pb2.ListConvenienceMethodsReply()

            for manifest in manifests:
                for cm in manifest["convenience_methods"]:
                    item = response.convenience_methods.add()
                    item.filename = cm["filename"]
                    item.contents = open(cm["path"]).read()
            REQUEST_COUNT.labels(
                "xos-core", "DynamicLoad", "GetConvenienceMethods", grpc.StatusCode.OK
            ).inc()
            return response

        except Exception as e:
            import traceback

            traceback.print_exc()
            REQUEST_COUNT.labels(
                "xos-core",
                "DynamicLoad",
                "GetConvenienceMethods",
                grpc.StatusCode.INTERNAL,
            ).inc()
            raise e
