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
print "testing basic secure List{{ object.camel() }}...",
c.stub.List{{ object.camel() }}(Empty())
print "Okay"
{%- endfor %}

# now try to login
c=grpc_client.InsecureClient("xos-core.cord.lab")
lr=grpc_client.LoginRequest()
lr.username="padmin@vicci.org"
lr.password="letmein"
session=c.utility.Login(lr)

c=grpc_client.SecureClient("xos-core.cord.lab", sessionid=session.sessionid)
{% for object in generator.all() %}
print "testing session secure List{{ object.camel() }}...",
c.stub.List{{ object.camel() }}(Empty())
print "Okay"
{%- endfor %}

