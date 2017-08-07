
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

print "orm_user_crud"

c=grpc_client.SecureClient("xos-core.cord.lab", username=USERNAME, password=PASSWORD)

# create a new user and save it
u=c.xos_orm.User.objects.new()
assert(u.id==0)
import random, string
u.email=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
u.site_id=1
u.save()

# when we created the user, he should be assigned an id
orig_id = u.id
assert(orig_id!=0)

# site object should be populated
assert(u.site is not None)

# site object should have a backpointer to user
u_all = u.site.users.all()
u_all = [x for x in u_all if x.email == u.email]
assert(len(u_all)==1)

# update the user
u.password="foobar"
u.save()

# update should not have changed it
assert(u.id==orig_id)

# check a listall and make sure the user is listed
u_all = c.xos_orm.User.objects.all()
u_all = [x for x in u_all if x.email == u.email]
assert(len(u_all)==1)
u2 = u_all[0]
assert(u2.id == u.id)

# get and make sure the password was updated
u3 = c.xos_orm.User.objects.get(id=orig_id)
assert(u3.password=="foobar")

# delete the user
u3.delete()

# make sure it is deleted
u_all = c.xos_orm.User.objects.all()
u_all = [x for x in u_all if x.email == u.email]
assert(len(u_all)==0)

print "    okay"

