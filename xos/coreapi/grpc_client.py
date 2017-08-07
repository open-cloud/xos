
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
import grpc
import orm
from protos.common_pb2 import *
from protos.xos_pb2 import *
from protos.utility_pb2 import *
from protos import xos_pb2_grpc, modeldefs_pb2_grpc, utility_pb2_grpc
from google.protobuf.empty_pb2 import Empty
from grpc import metadata_call_credentials, ChannelCredentials, composite_channel_credentials, ssl_channel_credentials

SERVER_CA="/usr/local/share/ca-certificates/local_certs.crt"

class UsernamePasswordCallCredentials(grpc.AuthMetadataPlugin):
  """Metadata wrapper for raw access token credentials."""
  def __init__(self, username, password):
        self._username = username
        self._password = password
  def __call__(self, context, callback):
        basic_auth = "Basic %s" % base64.b64encode("%s:%s" % (self._username, self._password))
        metadata = (('Authorization', basic_auth),)
        callback(metadata, None)

class SessionIdCallCredentials(grpc.AuthMetadataPlugin):
  """Metadata wrapper for raw access token credentials."""
  def __init__(self, sessionid):
        self._sessionid = sessionid
  def __call__(self, context, callback):
        metadata = (('x-xossession', self._sessionid),)
        callback(metadata, None)

class XOSClient(object):
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port

class InsecureClient(XOSClient):
    def __init__(self, hostname, port=50055):
        super(InsecureClient,self).__init__(hostname, port)
        self.channel = grpc.insecure_channel("%s:%d" % (self.hostname, self.port))
        self.stub = xos_pb2_grpc.xosStub(self.channel)
        self.modeldefs = modeldefs_pb2_grpc.modeldefsStub(self.channel)
        self.utility = utility_pb2_grpc.utilityStub(self.channel)

        self.xos_orm = orm.ORMStub(self.stub, "xos")

class SecureClient(XOSClient):
    def __init__(self, hostname, port=50051, cacert=SERVER_CA, username=None, password=None, sessionid=None):
        super(SecureClient,self).__init__(hostname, port)

        server_ca = open(cacert,"r").read()
        if (sessionid):
            call_creds = metadata_call_credentials(SessionIdCallCredentials(sessionid))
        else:
            call_creds = metadata_call_credentials(UsernamePasswordCallCredentials(username, password))
        chan_creds = ssl_channel_credentials(server_ca)
        chan_creds = composite_channel_credentials(chan_creds, call_creds)

        self.channel = grpc.secure_channel("%s:%d" % (self.hostname, self.port), chan_creds)
        self.stub = xos_pb2_grpc.xosStub(self.channel)
        self.modeldefs = modeldefs_pb2_grpc.modeldefsStub(self.channel)
        self.utility = utility_pb2_grpc.utilityStub(self.channel)

        self.xos_orm = orm.ORMStub(self.stub, "xos")

def main():  # self-test
    client = InsecureClient("xos-core.cord.lab")
    print client.stub.ListUser(Empty())

    client = SecureClient("xos-core.cord.lab", username="padmin@vicci.org", password="letmein")
    print client.stub.ListUser(Empty())

if __name__=="__main__":
    main()

