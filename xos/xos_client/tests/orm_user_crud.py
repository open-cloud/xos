
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

from xosapi import xos_grpc_client

def test_callback():
    print "TEST: orm_user_crud"

    c = xos_grpc_client.coreclient

    # create a new user and save it
    u=c.xos_orm.User.objects.new()
    assert(u.id==0)
    import random, string
    u.email=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
    u.site=c.xos_orm.Site.objects.all()[0]
    u.save()

    # when we created the user, he should be assigned an id
    orig_id = u.id
    assert(orig_id!=0)

    # invalidate u.site so it's reloaded from the server
    u.invalidate_cache("site")

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

    # try a partial update
    u3.password = "should_not_change"
    u3.firstname = "new_first_name"
    u3.lastname = "new_last_name"
    u3.save(update_fields = ["firstname", "lastname"])

    # get and make sure the password was not updated, but first and last name were
    u4 = c.xos_orm.User.objects.get(id=orig_id)
    assert(u4.password=="foobar")
    assert(u4.firstname == "new_first_name")
    assert(u4.lastname == "new_last_name")

    # delete the user
    u4.delete()

    # make sure it is deleted
    u_all = c.xos_orm.User.objects.all()
    u_all = [x for x in u_all if x.email == u.email]
    assert(len(u_all)==0)

    print "    okay"

xos_grpc_client.start_api_parseargs(test_callback)

