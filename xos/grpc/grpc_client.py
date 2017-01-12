import base64
import grpc
from protos.common_pb2 import *
from protos.xos_pb2 import *
from protos import xos_pb2_grpc
from google.protobuf.empty_pb2 import Empty
from grpc import metadata_call_credentials, ChannelCredentials, composite_channel_credentials, ssl_channel_credentials

class UsernamePasswordCallCredentials(grpc.AuthMetadataPlugin):
  """Metadata wrapper for raw access token credentials."""
  def __init__(self, username, password):
        self._username = username
        self._password = password
  def __call__(self, context, callback):
        basic_auth = "Basic %s" % base64.b64encode("%s:%s" % (self._username, self._password))
        metadata = (('Authorization', basic_auth),)
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

class SecureClient(XOSClient):
    def __init__(self, hostname, port=50051, cacert="certs/ca.crt", username=None, password=None):
        super(SecureClient,self).__init__(hostname, port)

        server_ca = open(cacert,"r").read()
        call_creds = metadata_call_credentials(UsernamePasswordCallCredentials(username, password))
        chan_creds = ssl_channel_credentials(server_ca)
        chan_creds = composite_channel_credentials(chan_creds, call_creds)

        self.channel = grpc.secure_channel("%s:%d" % (self.hostname, self.port), chan_creds)
        self.stub = xos_pb2_grpc.xosStub(self.channel)

def main():  # self-test
    client = InsecureClient("xos-core.cord.lab")
    print client.stub.ListUser(Empty())

    client = SecureClient("xos-core.cord.lab", username="padmin@vicci.org", password="letmein")
    print client.stub.ListUser(Empty())

if __name__=="__main__":
    main()

