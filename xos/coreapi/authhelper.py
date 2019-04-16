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

from __future__ import print_function
import base64
from importlib import import_module
import threading
import time

from django.conf import settings
from django.contrib.auth import authenticate as django_authenticate
from core.models import Site, User, XOSBase
from xos.exceptions import (
    XOSNotAuthenticated,
    XOSPermissionDenied,
    XOSNotFound,
    XOSValidationError,
)

from xosconfig import Config
from multistructlog import create_logger

log = create_logger(Config().get("logging"))


SessionStore = import_module(settings.SESSION_ENGINE).SessionStore


class CachedAuthenticator(object):
    """ Django Authentication is very slow (~ 10 ops/second), so cache
        authentication results and reuse them.
    """

    def __init__(self):
        self.cached_creds = {}
        self.timeout = 10  # keep cache entries around for 10s
        # lock to keep multiple callers from trimming at the same time
        self.lock = threading.Lock()

    def authenticate(self, username, password):
        self.trim()

        key = "%s:%s" % (username, password)
        cred = self.cached_creds.get(key, None)
        if cred:
            user = User.objects.filter(id=cred["user_id"])
            if user:
                user = user[0]
                # print "cached authenticated %s:%s as %s" % (username,
                # password, user)
                return user

        user = django_authenticate(username=username, password=password)
        if user:
            # print "django authenticated %s:%s as %s" % (username, password,
            # user)
            self.cached_creds[key] = {
                "timeout": time.time() + self.timeout,
                "user_id": user.id,
            }

        return user

    def trim(self):
        """ Delete all cache entries that have expired """
        self.lock.acquire()
        for (k, v) in list(self.cached_creds.items()):
            if time.time() > v["timeout"]:
                del self.cached_creds[k]
        self.lock.release()


cached_authenticator = CachedAuthenticator()


class XOSAuthHelperMixin(object):
    def authenticate(self, context, required=True):
        for (k, v) in context.invocation_metadata():
            if k.lower() == "authorization":
                (method, auth) = v.split(" ", 1)
                if method.lower() == "basic":
                    auth = base64.b64decode(auth)
                    (username, password) = auth.split(":")
                    user = cached_authenticator.authenticate(
                        username=username, password=password
                    )
                    if not user:
                        raise XOSPermissionDenied(
                            "failed to authenticate %s:%s" % (username, password)
                        )
                    return user
            elif k.lower() == "x-xossession":
                s = SessionStore(session_key=v)
                id = s.get("_auth_user_id", None)
                if not id:
                    raise XOSPermissionDenied("failed to authenticate token %s" % v)
                user = User.objects.get(id=id)
                return user

        if required:
            raise XOSNotAuthenticated("This API requires authentication")

        return None
