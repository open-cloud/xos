import base64
import functools
import grpc
import orm
import os
import pdb
import sys
from google.protobuf.empty_pb2 import Empty
from grpc import metadata_call_credentials, ChannelCredentials, composite_channel_credentials, ssl_channel_credentials

# fix up sys.path for chameleon
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path = [currentdir] + sys.path

import chameleon.grpc_client.grpc_client as chameleon_client

from twisted.internet import reactor


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

class XOSClient(chameleon_client.GrpcClient):
    # We layer our own reconnect_callback functionality so we can setup the
    # ORM before calling reconnect_callback.

    def set_reconnect_callback(self, reconnect_callback):
        self.reconnect_callback2 = reconnect_callback
        return self

    def reconnected(self):
        for api in ['modeldefs', 'utility', 'xos']:
            pb2_file_name = os.path.join(self.work_dir, api + "_pb2.py")
            pb2_grpc_file_name = os.path.join(self.work_dir, api + "_pb2_grpc.py")

            if os.path.exists(pb2_file_name) and os.path.exists(pb2_grpc_file_name):
                orig_sys_path = sys.path
                try:
                    sys.path.append(self.work_dir)
                    m_protos = __import__(api + "_pb2")
                    m_grpc = __import__(api + "_pb2_grpc")
                finally:
                    sys.path = orig_sys_path

                stub_class = getattr(m_grpc, api+"Stub")

                setattr(self, api, stub_class(self.channel))
            else:
                print >> sys.stderr, "failed to locate api", api

        if hasattr(self, "xos"):
            self.xos_orm = orm.ORMStub(self.xos, "xos")

        if self.reconnect_callback2:
            self.reconnect_callback2()


class InsecureClient(XOSClient):
    def __init__(self, consul_endpoint=None, work_dir="/tmp/xos_grpc_protos", endpoint='localhost:50055', reconnect_callback=None):
        super(InsecureClient,self).__init__(consul_endpoint, work_dir, endpoint, self.reconnected)

        self.reconnect_callback2 = reconnect_callback

class SecureClient(XOSClient):
    def __init__(self, consul_endpoint=None, work_dir="/tmp/xos_grpc_protos", endpoint='localhost:50055', reconnect_callback=None, cacert=SERVER_CA, username=None, password=None, sessionid=None):
        server_ca = open(cacert,"r").read()
        if (sessionid):
            call_creds = metadata_call_credentials(SessionIdCallCredentials(sessionid))
        else:
            call_creds = metadata_call_credentials(UsernamePasswordCallCredentials(username, password))
        chan_creds = ssl_channel_credentials(server_ca)
        chan_creds = composite_channel_credentials(chan_creds, call_creds)

        super(SecureClient,self).__init__(consul_endpoint, work_dir, endpoint, self.reconnected, chan_creds)

        self.reconnect_callback2 = reconnect_callback

# -----------------------------------------------------------------------------
# Self test
# -----------------------------------------------------------------------------

def insecure_callback(client):
    print "insecure self_test start"
    print client.xos_orm.User.objects.all()
    print "insecure self_test done"

    # now start the next test
    client.stop()
    reactor.callLater(0, start_secure_test)

def start_insecure_test():
    client = InsecureClient(endpoint="xos-core.cord.lab:50055")
    client.set_reconnect_callback(functools.partial(insecure_callback, client))
    client.start()

def secure_callback(client):
    print "secure self_test start"
    print client.xos_orm.User.objects.all()
    print "secure self_test done"
    reactor.stop()

def start_secure_test():
    client = SecureClient(endpoint="xos-core.cord.lab:50051", username="xosadmin@opencord.org", password="BQSPdpRsR0MrrZ9u7SPe")
    client.set_reconnect_callback(functools.partial(secure_callback, client))
    client.start()

def main():
    reactor.callLater(0, start_insecure_test)

    reactor.run()

if __name__=="__main__":
    main()

