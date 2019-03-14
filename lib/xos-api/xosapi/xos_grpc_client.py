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

from __future__ import absolute_import, print_function

import argparse
import base64
import functools
import inspect
import os
import sys

from google.protobuf.empty_pb2 import Empty

import grpc
from grpc import (composite_channel_credentials, metadata_call_credentials,
                  ssl_channel_credentials)

from twisted.internet import reactor
from xosconfig import Config

from xosapi import orm
import xosapi.chameleon_client.grpc_client as chameleon_client

from multistructlog import create_logger
log = create_logger(Config().get("logging"))

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path = [currentdir] + sys.path

SERVER_CA = "/usr/local/share/ca-certificates/local_certs.crt"


class UsernamePasswordCallCredentials(grpc.AuthMetadataPlugin):
    """Metadata wrapper for raw access token credentials."""

    def __init__(self, username, password):
        self._username = username
        self._password = password

    def __call__(self, context, callback):
        basic_auth = "Basic %s" % base64.b64encode(
            "%s:%s" % (self._username, self._password)
        )
        metadata = (("authorization", basic_auth),)
        callback(metadata, None)


class SessionIdCallCredentials(grpc.AuthMetadataPlugin):
    """Metadata wrapper for raw access token credentials."""

    def __init__(self, sessionid):
        self._sessionid = sessionid

    def __call__(self, context, callback):
        metadata = (("x-xossession", self._sessionid),)
        callback(metadata, None)


class XOSClient(chameleon_client.GrpcClient):
    # We layer our own reconnect_callback functionality so we can setup the
    # ORM before calling reconnect_callback.

    def set_reconnect_callback(self, reconnect_callback):
        self.reconnect_callback2 = reconnect_callback

        return self

    def request_convenience_methods(self):

        convenience_methods_dir = "/var/run/xosapi/convenience"
        if not os.path.exists(convenience_methods_dir):
            log.info("Creating convenience methods directory", convenience_methods_dir=convenience_methods_dir)
            os.makedirs(convenience_methods_dir)

        try:
            response = self.dynamicload.GetConvenienceMethods(Empty())

            if response:
                log.info(
                    "Saving convenience methods",
                    methods=[m.filename for m in response.convenience_methods],
                )

                for cm in response.convenience_methods:
                    log.debug("Saving convenience method", method=cm.filename)
                    save_path = os.path.join(convenience_methods_dir, cm.filename)
                    open(save_path, "w").write(cm.contents)
            else:
                log.exception(
                    "Cannot load convenience methods, restarting the synchronzier"
                )
                os.execv(sys.executable, ["python"] + sys.argv)

        except grpc._channel._Rendezvous as e:
            code = e.code()
            if code == grpc.StatusCode.UNAVAILABLE:
                # NOTE if the core is not available, restart the synchronizer
                os.execv(sys.executable, ["python"] + sys.argv)

    def reconnected(self):
        for api in ["modeldefs", "utility", "xos", "dynamicload"]:
            pb2_file_name = os.path.join(self.work_dir, api + "_pb2.py")
            pb2_grpc_file_name = os.path.join(self.work_dir, api + "_pb2_grpc.py")

            if os.path.exists(pb2_file_name) and os.path.exists(pb2_grpc_file_name):
                orig_sys_path = sys.path
                try:
                    sys.path.append(self.work_dir)
                    m_protos = __import__(api + "_pb2")
                    # reload(m_protos)
                    m_grpc = __import__(api + "_pb2_grpc")
                    # reload(m_grpc)
                finally:
                    sys.path = orig_sys_path

                stub_class = getattr(m_grpc, api + "Stub")

                setattr(self, api, stub_class(self.channel))
                setattr(self, api + "_pb2", m_protos)
            else:
                print("failed to locate api", api, file=sys.stderr)

        if hasattr(self, "xos"):
            self.xos_orm = orm.ORMStub(self.xos, self.xos_pb2, "xos")

        # ask the core for the convenience methods
        self.request_convenience_methods()

        # Load convenience methods after reconnect
        orm.import_convenience_methods()

        if self.reconnect_callback2:
            self.reconnect_callback2()


class InsecureClient(XOSClient):
    def __init__(
        self,
        consul_endpoint=None,
        work_dir="/tmp/xos_grpc_protos",
        endpoint="localhost:50055",
        reconnect_callback=None,
    ):
        super(InsecureClient, self).__init__(
            consul_endpoint, work_dir, endpoint, self.reconnected
        )

        self.reconnect_callback2 = reconnect_callback


class SecureClient(XOSClient):
    def __init__(
        self,
        consul_endpoint=None,
        work_dir="/tmp/xos_grpc_protos",
        endpoint="localhost:50055",
        reconnect_callback=None,
        cacert=SERVER_CA,
        username=None,
        password=None,
        sessionid=None,
    ):
        server_ca = open(cacert, "r").read()
        if sessionid:
            call_creds = metadata_call_credentials(SessionIdCallCredentials(sessionid))
        else:
            call_creds = metadata_call_credentials(
                UsernamePasswordCallCredentials(username, password)
            )
        chan_creds = ssl_channel_credentials(server_ca)
        chan_creds = composite_channel_credentials(chan_creds, call_creds)

        super(SecureClient, self).__init__(
            consul_endpoint, work_dir, endpoint, self.reconnected, chan_creds
        )

        self.reconnect_callback2 = reconnect_callback


# -----------------------------------------------------------------------------
# Wrappers for easy setup for test cases, etc
# -----------------------------------------------------------------------------


def parse_args():
    parser = argparse.ArgumentParser()

    defs = {
        "grpc_insecure_endpoint": "xos-core.cord.lab:50055",
        "grpc_secure_endpoint": "xos-core.cord.lab:50051",
        "config": "/opt/xos/config.yml",
    }

    _help = "Path to the config file (default: %s)" % defs["config"]
    parser.add_argument(
        "-C",
        "--config",
        dest="config",
        action="store",
        default=defs["config"],
        help=_help,
    )

    _help = (
        "gRPC insecure end-point to connect to. It is a direct",
        ". (default: %s" % defs["grpc_insecure_endpoint"],
    )
    parser.add_argument(
        "-G",
        "--grpc-insecure-endpoint",
        dest="grpc_insecure_endpoint",
        action="store",
        default=defs["grpc_insecure_endpoint"],
        help=_help,
    )

    _help = (
        "gRPC secure end-point to connect to. It is a direct",
        ". (default: %s" % defs["grpc_secure_endpoint"],
    )
    parser.add_argument(
        "-S",
        "--grpc-secure-endpoint",
        dest="grpc_secure_endpoint",
        action="store",
        default=defs["grpc_secure_endpoint"],
        help=_help,
    )

    parser.add_argument(
        "-u", "--username", dest="username", action="store", default=None, help=_help
    )

    parser.add_argument(
        "-p", "--password", dest="password", action="store", default=None, help=_help
    )

    _help = "omit startup banner log lines"
    parser.add_argument(
        "-n",
        "--no-banner",
        dest="no_banner",
        action="store_true",
        default=False,
        help=_help,
    )

    _help = "suppress debug and info logs"
    parser.add_argument("-q", "--quiet", dest="quiet", action="count", help=_help)

    _help = "enable verbose logging"
    parser.add_argument("-v", "--verbose", dest="verbose", action="count", help=_help)

    args = parser.parse_args()

    return args


def coreclient_reconnect(client, reconnect_callback, *args, **kwargs):
    global coreapi

    coreapi = coreclient.xos_orm

    if reconnect_callback:
        reconnect_callback(*args, **kwargs)

    reactor.stop()


def start_api(reconnect_callback, *args, **kwargs):
    global coreclient

    if kwargs.get("username", None):
        coreclient = SecureClient(*args, **kwargs)
    else:
        coreclient = InsecureClient(*args, **kwargs)

    coreclient.set_reconnect_callback(
        functools.partial(coreclient_reconnect, coreclient, reconnect_callback)
    )
    coreclient.start()

    reactor.run()


def start_api_parseargs(reconnect_callback):
    """ This function is an entrypoint for tests and other simple programs to
        setup the API and get a callback when the API is ready.
    """

    args = parse_args()

    if args.username:
        start_api(
            reconnect_callback,
            endpoint=args.grpc_secure_endpoint,
            username=args.username,
            password=args.password,
        )
    else:
        start_api(reconnect_callback, endpoint=args.grpc_insecure_endpoint)


# -----------------------------------------------------------------------------
# Self test
# -----------------------------------------------------------------------------


def insecure_callback(client):
    print("insecure self_test start")
    print(client.xos_orm.User.objects.all())
    print("insecure self_test done")

    # now start the next test
    client.stop()
    reactor.callLater(0, start_secure_test)


def start_insecure_test():
    client = InsecureClient(endpoint="xos-core:50055")
    client.set_reconnect_callback(functools.partial(insecure_callback, client))
    client.start()


def secure_callback(client):
    print("secure self_test start")
    print(client.xos_orm.User.objects.all())
    print("secure self_test done")
    reactor.stop()


def start_secure_test():
    client = SecureClient(
        endpoint="xos-core:50051", username="admin@opencord.org", password="letmein"
    )
    client.set_reconnect_callback(functools.partial(secure_callback, client))
    client.start()


def main():
    reactor.callLater(0, start_insecure_test)

    reactor.run()


if __name__ == "__main__":
    main()
