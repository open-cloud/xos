import grpc_client
from grpc_client import Empty
from testconfig import *

c=grpc_client.InsecureClient("xos-core.cord.lab")

{% for object in generator.all() %}
print "testing insecure List{{ object.camel() }}...",
c.stub.List{{ object.camel() }}(Empty())
print "Okay"
{%- endfor %}

c=grpc_client.SecureClient("xos-core.cord.lab", username=USERNAME, password=PASSWORD)

{% for object in generator.all() %}
print "testing basic secure List{{ object.camel() }}...",
c.stub.List{{ object.camel() }}(Empty())
print "Okay"
{%- endfor %}

# now try to login
c=grpc_client.InsecureClient("xos-core.cord.lab")
lr=grpc_client.LoginRequest()
lr.username=USERNAME
lr.password=PASSWORD
session=c.utility.Login(lr)

c=grpc_client.SecureClient("xos-core.cord.lab", sessionid=session.sessionid)
{% for object in generator.all() %}
print "testing session secure List{{ object.camel() }}...",
c.stub.List{{ object.camel() }}(Empty())
print "Okay"
{%- endfor %}

c=grpc_client.SecureClient("xos-core.cord.lab", sessionid=session.sessionid)
{% for object in generator.all() %}
print "testing session secure xos_orm.{{ object.camel() }}.objects.all() ...",
c.xos_orm.{{ object.camel() }}.objects.all()
print "Okay"
{%- endfor %}

