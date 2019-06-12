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

from __future__ import print_function
from apistats import REQUEST_COUNT
import time
import grpc
from django import db

from xos.exceptions import (
    XOSNotAuthenticated,
    XOSPermissionDenied,
    XOSNotFound,
    XOSValidationError,
)

from xosconfig import Config
from multistructlog import create_logger

log = create_logger(Config().get("logging"))

# This decorator causes issues with unit tests, so provide a means to disable it.
disable_check_db_connection_decorator = False


def translate_exceptions(model, method):
    """ this decorator translates XOS exceptions to grpc status codes """

    def decorator(function):
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except Exception as e:

                import traceback

                tb = traceback.format_exc()
                print(tb)
                # TODO can we propagate it over the APIs?

                if "context" in kwargs:
                    context = kwargs["context"]
                else:
                    context = args[2]

                if hasattr(e, "json_detail"):
                    context.set_details(e.json_detail)
                elif hasattr(e, "detail"):
                    context.set_details(e.detail)

                if isinstance(e, XOSPermissionDenied):
                    REQUEST_COUNT.labels(
                        "xos-core", model, method, grpc.StatusCode.PERMISSION_DENIED
                    ).inc()
                    context.set_code(grpc.StatusCode.PERMISSION_DENIED)
                elif isinstance(e, XOSValidationError):
                    REQUEST_COUNT.labels(
                        "xos-core", model, method, grpc.StatusCode.INVALID_ARGUMENT
                    ).inc()
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                elif isinstance(e, XOSNotAuthenticated):
                    REQUEST_COUNT.labels(
                        "xos-core", model, method, grpc.StatusCode.UNAUTHENTICATED
                    ).inc()
                    context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                elif isinstance(e, XOSNotFound):
                    REQUEST_COUNT.labels(
                        "xos-core", model, method, grpc.StatusCode.NOT_FOUND
                    ).inc()
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                raise

        return wrapper

    return decorator


bench_tStart = time.time()
bench_ops = 0


def benchmark(function):
    """ this decorator will report gRPC benchmark statistics every 10 seconds """

    def wrapper(*args, **kwargs):
        global bench_tStart
        global bench_ops
        result = function(*args, **kwargs)
        bench_ops = bench_ops + 1
        elap = time.time() - bench_tStart
        if elap >= 10:
            print("performance %d" % (bench_ops / elap))
            bench_ops = 0
            bench_tStart = time.time()
        return result

    return wrapper


def require_authentication(function):
    def wrapper(self, request, context):
        self.authenticate(context, required=True)
        result = function(self, request, context)
        return result

    return wrapper


def check_db_connection(function):
    """ Check that the database connection is not in "already closed" state.
        This tends to happen when postgres is restarted. Connections will persist
        in this state throwing "connection already closed" errors until the
        old connections are disposed of.
    """
    def wrapper(self, *args, **kwargs):
        if not disable_check_db_connection_decorator:
            try:
                db.connection.cursor()
            except Exception as e:
                if "connection already closed" in str(e):
                    log.warning("check_db_connection: connection already closed")
                    try:
                        db.close_old_connections()
                        log.info("check_db_connection: removed old connections")
                    except Exception as e:
                        log.exception("check_db_connection: we failed to fix the failure", e=e)
                        raise
                else:
                    raise

        result = function(self, *args, **kwargs)
        return result

    return wrapper
