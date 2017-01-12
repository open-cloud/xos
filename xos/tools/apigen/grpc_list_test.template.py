import grpc_client
from grpc_client import Empty

c=grpc_client.InsecureClient("xos-core.cord.lab")

{% for object in generator.all() %}
print "testing insecure List{{ object.camel() }}...",
c.stub.List{{ object.camel() }}(Empty())
print "Okay"
{%- endfor %}

c=grpc_client.SecureClient("xos-core.cord.lab", username="padmin@vicci.org", password="letmein")

{% for object in generator.all() %}
print "testing secure List{{ object.camel() }}...",
c.stub.List{{ object.camel() }}(Empty())
print "Okay"
{%- endfor %}

