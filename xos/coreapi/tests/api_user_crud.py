
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

