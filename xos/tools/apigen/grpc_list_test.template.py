import grpc
from protos import common_pb2
from protos import xos_pb2
from protos import xos_pb2_grpc
from google.protobuf.empty_pb2 import Empty

channel = grpc.insecure_channel("localhost:50055")
stub = xos_pb2_grpc.xosStub(channel)

{% for object in generator.all() %}
print "List{{ object.camel() }}...",
stub.List{{ object.camel() }}(Empty())
print "Okay"
{%- endfor %}


