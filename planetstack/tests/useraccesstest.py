import inspect
import json
import os
import requests
import sys

from operator import itemgetter, attrgetter

REST_API="http://node43.princeton.vicci.org:8000/plstackapi/"
USERS_API = REST_API + "users/"
SLICES_API = REST_API + "slices/"
SITES_API = REST_API + "sites/"
SITEPRIV_API = REST_API + "site_privileges/"
SLICEPRIV_API = REST_API + "slice_memberships/"
SITEROLE_API = REST_API + "site_roles/"

username = sys.argv[1]
password = sys.argv[2]

opencloud_auth=(username, password)
admin_auth=("scott@onlab.us", "letmein")

def fail_unless(x, msg):
    if not x:
        (frame, filename, line_number, function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
        print "FAIL (%s:%d)" % (function_name, line_number), msg


print "downloading objects using admin"
r = requests.get(USERS_API + "?no_hyperlinks=1", auth=admin_auth)
allUsers = r.json()
r = requests.get(SLICES_API + "?no_hyperlinks=1", auth=admin_auth)
allSlices = r.json()
r = requests.get(SITES_API + "?no_hyperlinks=1", auth=admin_auth)
allSites = r.json()
r = requests.get(SITEPRIV_API + "?no_hyperlinks=1", auth=admin_auth)
allSitePriv = r.json()
r = requests.get(SLICEPRIV_API + "?no_hyperlinks=1", auth=admin_auth)
allSlicePriv = r.json()
r = requests.get(SITEROLE_API + "?no_hyperlinks=1", auth=admin_auth)
allSiteRole = r.json()

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

def flip_phone(user):
    if user["phone"] == "123":
        user["phone"] = "456"
    else:
        user["phone"] = "123"

print "  loaded user:%d slice:%d, site:%d, site_priv:%d slice_priv:%d" % (len(allUsers), len(allSlices), len(allSites), len(allSitePriv), len(allSlicePriv))

# get our own user record

r = requests.get(USERS_API + "?email=%s&no_hyperlinks" % username, auth=opencloud_auth)
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

for user in allUsers:
    user = requests.get(USERS_API + str(user["id"]) + "/", auth=admin_auth).json()
    flip_phone(user)
    r = requests.put(USERS_API + str(user["id"]) +"/", data=user, auth=opencloud_auth)
    if should_see_user(myself, user):
        fail_unless(r.status_code==200, "failed to change phone number on %s" % user["email"])
    else:
        # XXX: this is failing, but for the wrong reason
        fail_unless(r.status_code!=200, "was able to change phone number on %s but shouldn't have" % user["email"])

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





