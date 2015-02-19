""" useraccesstest.py

    This is a basic REST API permission test. Call it with a username and a
    password, and it will try to read and update some user and slice object,
    and report if something is broken.

    This is not an exhaustive test.
"""


import inspect
import json
import os
import requests
import sys
import time
from urllib  import urlencode

from operator import itemgetter, attrgetter

if (len(sys.argv)!=6):
    print "syntax: usertest <hostname> <username> <password> <admin_username> <admin_password>"
    sys.exit(-1)

hostname = sys.argv[1]
username = sys.argv[2]
password = sys.argv[3]

opencloud_auth=(username, password)
admin_auth=(sys.argv[4], sys.argv[5])

REST_API="http://%s:8000/xos/" % hostname
USERS_API = REST_API + "users/"
SLICES_API = REST_API + "slices/"
SITES_API = REST_API + "sites/"
SITEPRIV_API = REST_API + "siteprivileges/"
SLICEPRIV_API = REST_API + "slice_privileges/"
SITEROLE_API = REST_API + "site_roles/"
SLICEROLE_API = REST_API + "slice_roles/"

TEST_USER_EMAIL = "test" + str(time.time()) + "@test.com" # in case observer not running, objects won't be purged, so use unique email

def fail_unless(x, msg):
    if not x:
        (frame, filename, line_number, function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
        print "FAIL (%s:%d)" % (function_name, line_number), msg

print "downloading objects using admin"
r = requests.get(USERS_API + "?no_hyperlinks=1", auth=admin_auth)
fail_unless(r.status_code==200, "failed to get users")
allUsers = r.json()
r = requests.get(SLICES_API + "?no_hyperlinks=1", auth=admin_auth)
fail_unless(r.status_code==200, "failed to get slices")
allSlices = r.json()
r = requests.get(SITES_API + "?no_hyperlinks=1", auth=admin_auth)
allSites = r.json()
r = requests.get(SITEPRIV_API + "?no_hyperlinks=1", auth=admin_auth)
allSitePriv = r.json()
r = requests.get(SLICEPRIV_API + "?no_hyperlinks=1", auth=admin_auth)
allSlicePriv = r.json()
r = requests.get(SITEROLE_API + "?no_hyperlinks=1", auth=admin_auth)
allSiteRole = r.json()
r = requests.get(SLICEROLE_API + "?no_hyperlinks=1", auth=admin_auth)
allSliceRole = r.json()

def should_see_user(myself, otherUser):
    if myself["is_admin"]:
        return True
    if myself["id"] == otherUser["id"]:
        return True
    for sitePriv in allSitePriv:
        if (sitePriv["user"] == myself["id"]) and (sitePriv["site"] == otherUser["site"]):
            for role in allSiteRole:
                if role["role"]=="pi" and role["id"] == sitePriv["role"]:
                    return True
    return False

def should_see_slice(myself, slice):
    if myself["is_admin"]:
        return True
    for sitePriv in allSitePriv:
        if (sitePriv["user"] == myself["id"]) and (sitePriv["site"] == slice["site"]):
            for role in allSiteRole:
                if role["role"]=="pi" and role["id"] == sitePriv["role"]:
                    return True
    for slicePriv in allSlicePriv:
        if (slicePriv["user"] == myself["id"]) and (sitePriv["slice"] == slice["id"]):
            for role in allSliceRole:
                if role["role"]=="pi" and role["id"] == slicePriv["role"]:
                    return True
    return False

def flip_phone(user):
    if user["phone"] == "123":
        user["phone"] = "456"
    else:
        user["phone"] = "123"

def flip_desc(slice):
    if slice["description"] == "some_description":
        slice["description"] = "some_other_description"
    else:
        slice["description"] = "some_description"

def delete_user_if_exists(email):
    r = requests.get(USERS_API +"?email=%s" % email, auth=admin_auth)
    if r.status_code==200:
        user = r.json()
        if len(user)>0:
            user=user[0]
            r = requests.delete(USERS_API + str(user["id"]) + "/", auth=admin_auth)
            fail_unless(r.status_code==200, "failed to delete the test user")

print "  loaded user:%d slice:%d, site:%d, site_priv:%d slice_priv:%d" % (len(allUsers), len(allSlices), len(allSites), len(allSitePriv), len(allSlicePriv))

# get our own user record

r = requests.get(USERS_API + "?" + urlencode({"email": username, "no_hyperlinks": "1"}), auth=opencloud_auth)
fail_unless(r.status_code==200, "failed to get user %s" % username)
myself = r.json()
fail_unless(len(myself)==1, "wrong number of results when getting user %s" % username)
myself = myself[0]

# check to see that we see the users we should be able to

r = requests.get(USERS_API, auth=opencloud_auth)
myUsers = r.json()
for user in myUsers:
    fail_unless(should_see_user(myself, user), "saw user %s but we shouldn't have" % user["email"])
myUsersIds = [r["id"] for r in myUsers]
for user in allUsers:
    if should_see_user(myself, user):
        fail_unless(user["id"] in myUsersIds, "should have seen user %s but didnt" % user["email"])

# toggle the phone number on the users we should be able to

"""
for user in allUsers:
    user = requests.get(USERS_API + str(user["id"]) + "/", auth=admin_auth).json()
    flip_phone(user)
    r = requests.put(USERS_API + str(user["id"]) +"/", data=user, auth=opencloud_auth)
    if should_see_user(myself, user):
        fail_unless(r.status_code==200, "failed to change phone number on %s" % user["email"])
    else:
        # XXX: this is failing, but for the wrong reason
        fail_unless(r.status_code!=200, "was able to change phone number on %s but shouldn't have" % user["email"])

# try changing is_staff. We should be able to do it if we're an admin, but not
# otherwise.

for user in allUsers:
    user = requests.get(USERS_API + str(user["id"]) + "/", auth=admin_auth).json()
    user["is_staff"] = not user["is_staff"]
    r = requests.put(USERS_API + str(user["id"]) +"/", data=user, auth=opencloud_auth)
    if myself["is_admin"]:
        fail_unless(r.status_code==200, "failed to change is_staff on %s" % user["email"])
    else:
        # XXX: this is failing, but for the wrong reason
        fail_unless(r.status_code!=200, "was able to change is_staff on %s but shouldn't have" % user["email"])

    # put it back to false, in case we successfully changed it...
    user["is_staff"] = False
    r = requests.put(USERS_API + str(user["id"]) +"/", data=user, auth=opencloud_auth)
"""

# delete the TEST_USER_EMAIL if it exists
delete_user_if_exists(TEST_USER_EMAIL)

# XXX - enacted and policed should not be required

newUser = {"firstname": "test", "lastname": "1234", "email": TEST_USER_EMAIL, "password": "letmein", "site": allSites[0]["id"], "enacted": "2015-01-01T00:00", "policed": "2015-01-01T00:00"}
r = requests.post(USERS_API + "?no_hyperlinks=1", data=newUser, auth=opencloud_auth)
if myself["is_admin"]:
    fail_unless(r.status_code==200, "failed to create %s" % TEST_USER_EMAIL)
else:
    fail_unless(r.status_code!=200, "created %s but we shouldn't have been able to" % TEST_USER_EMAIL)

delete_user_if_exists(TEST_USER_EMAIL)

# now create it as admin
r = requests.post(USERS_API + "?no_hyperlinks=1", data=newUser, auth=admin_auth)
if (r.status_code!=201):
    print r.text
fail_unless(r.status_code==201, "failed to create %s as admin" % TEST_USER_EMAIL)

r = requests.get(USERS_API +"?" + urlencode({"email": TEST_USER_EMAIL}), auth=admin_auth)
fail_unless(r.status_code==200, "failed to get user %s" % TEST_USER_EMAIL)
user=r.json()[0]
r = requests.delete(USERS_API + str(user["id"]) + "/", auth=opencloud_auth)
if myself["is_admin"]:
    fail_unless(r.status_code==200, "failed to delete %s" % TEST_USER_EMAIL)
else:
    fail_unless(r.status_code!=200, "deleted %s but we shouldn't have been able to" % TEST_USER_EMAIL)

# slice tests

r = requests.get(SLICES_API, auth=opencloud_auth)
mySlices = r.json()

for slice in mySlices:
    fail_unless(should_see_slice(myself, slice), "saw slice %s but we shouldn't have" % slice["name"])
mySlicesIds = [r["id"] for r in mySlices]
for slice in allSlices:
    if should_see_slice(myself, slice):
        fail_unless(slice["id"] in mySliceIds, "should have seen slice %s but didnt" % slice["name"])

for slice in allSlices:
    slice = requests.get(SLICES_API + str(slice["id"]) + "/", auth=admin_auth).json()
    flip_desc(slice)
    r = requests.put(SLICES_API + str(slice["id"]) +"/", data=slice, auth=opencloud_auth)
    if should_see_slice(myself, slice):
        fail_unless(r.status_code==200, "failed to change desc on %s" % slice["name"])
    else:
        fail_unless(r.status_code!=200, "was able to change desc on %s but shouldn't have" % slice["name"])

print "Done."
