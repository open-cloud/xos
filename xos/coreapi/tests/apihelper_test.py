
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

# NOTE: This unit test requires django at this time due to dependencies in apihelper.py.  It must be run from inside
#       a django-supporting environment, such as the core or ui containers.

import os
import sys

sys.path.append("..")

if __name__ == "__main__":
    import django
    sys.path.append('/opt/xos')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")

import unittest
from mock import patch
import mock
import time

import apihelper

def side_effect_bad_password(*args, **kwargs):
    raise Exception()

class MockObject:
    def __init__(self, **kwargs):
        for (k,v) in kwargs.items():
            setattr(self, k, v)

class TestCachedAuthenticator(unittest.TestCase):
    @patch('apihelper.User.objects')
    @patch('apihelper.django_authenticate')
    def test_authenticate_notcached(self, mock_django_authenticate, mock_user_filter):
        the_user = MockObject(id=123, email="testuser@test.com", username="testuser@test.com", password="foobar")
        mock_django_authenticate.return_value = the_user
        mock_user_filter.return_value = [the_user]

        ca = apihelper.CachedAuthenticator()
        result = ca.authenticate("testuser@test.com", "foobar")
        self.assertTrue(result)

        mock_django_authenticate.assert_called()

    @patch('apihelper.User.objects')
    @patch('apihelper.django_authenticate')
    def test_authenticate_notcached_badpassword(self, mock_django_authenticate, mock_user_filter):
        the_user = MockObject(id=123, email="testuser@test.com", username="testuser@test.com", password="foobar")
        mock_django_authenticate.side_effect = side_effect_bad_password
        mock_user_filter.return_value = [the_user]

        ca = apihelper.CachedAuthenticator()
        with self.assertRaises(Exception) as e:
            result = ca.authenticate("testuser@test.com", "not_foobar")

        mock_django_authenticate.assert_called()

    @patch('apihelper.User.objects')
    @patch('apihelper.django_authenticate')
    def test_authenticate_cached(self, mock_django_authenticate, mock_user_filter):
        the_user = MockObject(id=123, email="testuser@test.com", username="testuser@test.com", password="foobar")
        mock_django_authenticate.return_value = the_user
        mock_user_filter.return_value = [the_user]

        ca = apihelper.CachedAuthenticator()
        key = "%s:%s" % (the_user.username, the_user.password)
        ca.cached_creds[key] = {"timeout": time.time() + 10, "user_id": the_user.id}
        result = ca.authenticate("testuser@test.com", "foobar")
        self.assertTrue(result)

        mock_django_authenticate.assert_not_called()

    def test_trim(self):
        user_one = MockObject(id=123, email="testuser@test.com", username="testuser@test.com", password="foobar")
        user_two = MockObject(id=124, email="testuser4@test.com", username="testuser@test.com", password="foobar4")

        ca = apihelper.CachedAuthenticator()

        key_one = "%s:%s" % (user_one.username, user_one.password)
        ca.cached_creds[key_one] = {"timeout": time.time() - 11, "user_id": user_one.id}  # this will get trimmed

        key_two = "%s:%s" % (user_two.username, user_two.password)
        ca.cached_creds[key_two] = {"timeout": time.time() + 10, "user_id": user_two.id}  # this will not

        ca.trim()

        assert(len(ca.cached_creds.keys()) == 1)
        assert(ca.cached_creds.values()[0]["user_id"] == user_two.id)

if __name__ == '__main__':
    unittest.main()
