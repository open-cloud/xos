# gRPC API Usage Tutorial

The XOS gRPC API may be used directly for operating on objects in the XOS data model as an alternative to REST or TOSCA. This short tutorial will walk the reader through the necessary steps to generate protobufs and to create a working gRPC API client.

### Prerequisites

Several python packages need to be installed into your development environment. You may use our supplied [virtualenv](./unittest.html#setting-up-a-unit-testing-environment), or you can install the necessary packages directly into your development environment:

```shell
# for running xosgenx
sudo pip install plyxproto jinja2 pyyaml colorama

# for building protobufs
sudo pip install grpcio grpcio-tools

# install the xos-genx library (not currently available on pypi)
cd ~/cord/orchestration/xos/lib/xos-genx
sudo python ./setup.py install
```

This guide assumes that you have checked out CORD using the repo tool into the directory `~/cord`. It is also assumed that you have a working SEBA installation that uses the `att-workflow` profile.

### Build common protobufs

There are a number of common protobufs that are referenced by the XOS API that need to be generated. This can be done as follows:

```shell
cd ~/cord/orchestration/xos/xos/coreapi/protos
make
```

Note that you may want to clean these up (`make clean`) after you've completed this tutorial, particularly if you plan on building any XOS docker containers from your build environment.

### Generating and build protobufs and gRPC from a subset of the XOS API

The XOS API is relatively large, but if you want to only operate over a subset of it, there are options that can be used with xosgenx. Here's an example:

```shell
mkdir -p ~/cord/sample_client
cd ~/cord/sample_client
xosgenx --target protoapi.xtarget --include-apps volt --include-apps rcord --include-apps att-workflow-driver --include-apps fabric-crossconnect  ~/cord/orchestration/xos/xos/core/models/core.xproto ~/cord/orchestration/xos-services/olt-service/xos/synchronizer/models/volt.xproto ~/cord/orchestration/xos-services/att-workflow-driver/xos/synchronizer/models/att-workflow-driver.xproto ~/cord/orchestration/xos-services/fabric-crossconnect/xos/synchronizer/models/fabric-crossconnect.xproto ~/cord/orchestration/xos-services/rcord/xos/synchronizer/models/rcord.xproto > ~/cord/sample_client/seba.proto
```

Note that it's necessary to supply the source xproto files that you're going to use. For this example, we've provided a list that includes popular SEBA services. We've also included the core xprotos, since they include necessary base classes for the services.

The `--include-apps` directive is used to filter which apps are included in the output. In this example, we've included all apps present in the source files, *excluding* the core, as the core includes many models that we aren't directly interested in.

It's also time to copy the common protobuf stubs into your working directory:

```shell
cp ~/cord/orchestration/xos/xos/coreapi/protos/*_pb2*.py ~/cord/sample_client/
```

Finally, we can build our custom protobufs:

```shell
cd ~/cord/sample-client
COMMON_PROTO_DIR=`realpath ~/cord/orchestration/xos/xos/coreapi/protos`
python -m grpc_tools.protoc -I. -I$COMMON_PROTO_DIR --python_out=. --grpc_python_out=. seba.proto
```

This will generate `seba_pb2.py` and `seba_pb2_grpc.py`, and they will be residing alongside the common protobuf stubs that we copied into our working directory earlier.

### Get the ca-cert-chain

In order to use the gRPC API, we need to have a certificate that we can use to talk to the core. That certificate chain is located in the file `xos-core/values.yaml` in the `helm-charts` repositry. You'll need to locate the value `ca_cert_chain` in `values.yaml`, extract that value into a text file called `xos_core_ca_cert.in`, and then run the following:

```shell
base64 --decode xos_core_ca_cert.in > xos_core_ca_cert.out
```

The reason we had to base64 decode it is because secrets in kubernetes are always base64 encoded when they're placed into helm charts.

### Create and run the test client

Below is a simple test client:

```python
import base64
import grpc
import seba_pb2, seba_pb2_grpc

from grpc import metadata_call_credentials, ssl_channel_credentials, composite_channel_credentials
from google.protobuf.empty_pb2 import Empty

CACERT="xos_core_ca_cert.out"
USERNAME="admin@opencord.org"
PASSWORD="letmein"

class UsernamePasswordCallCredentials(grpc.AuthMetadataPlugin):
      """Metadata wrapper for raw access token credentials."""
      def __init__(self, username, password):
            self._username = username
            self._password = password
      def __call__(self, context, callback):
            basic_auth = "Basic %s" % base64.b64encode("%s:%s" % (self._username, self._password))
            metadata = (('authorization', basic_auth),)
            callback(metadata, None)

server_ca = open(CACERT,"r").read()
call_creds = metadata_call_credentials(UsernamePasswordCallCredentials(USERNAME, PASSWORD))
chan_creds = ssl_channel_credentials(server_ca)
chan_creds = composite_channel_credentials(chan_creds, call_creds)

with grpc.secure_channel('xos-core:30010', chan_creds) as channel:
    stub = seba_pb2_grpc.xosStub(channel)
    print stub.ListVOLTService(Empty())
```

Note that the name `xos-core` must resolve inside of the environment you will be using to run the client. The name `xos-core` is baked into the certificate, so it must be that named used, and no other name. When operating inside of a container, Kubernetes will usually have name resolution already provided, but if operating in a development environment outside of a container, it may be necessary to provide name resolution yourself, such as an entry in `/etc/hosts`.

Paste the above to a file, such as `client.py` and then run it (`python client.py`). The output should be a list of VOLTService currently in the data model. If there are no VOLTServices, then it'll emit an empty list.