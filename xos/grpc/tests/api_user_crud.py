import sys
sys.path.append("..")

import grpc_client
from testconfig import *

print "api_user_crud"

#c=grpc_client.InsecureClient("localhost")
c=grpc_client.SecureClient("xos-core.cord.lab", username=USERNAME, password=PASSWORD)
u=grpc_client.User()
import random, string
u.email=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
u.site_id=1
u2=c.stub.CreateUser(u)

# update the user
u2.password="foobar"
c.stub.UpdateUser(u2)

# do a listall and make sure user exists
u_all = c.stub.ListUser(grpc_client.Empty()).items
u_all = [x for x in u_all if x.email == u.email]
assert(len(u_all)==1)

u3=c.stub.GetUser(grpc_client.ID(id=u2.id))
assert(u3.id == u2.id)
assert(u3.password=="foobar")

c.stub.DeleteUser(grpc_client.ID(id=u3.id))

# make sure it is deleted
u_all = c.stub.ListUser(grpc_client.Empty()).items
u_all = [x for x in u_all if x.email == u.email]
assert(len(u_all)==0)

print "    okay"

