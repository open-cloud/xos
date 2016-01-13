#!/usr/bin/env python
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
import json
from django.forms.models import model_to_dict

from core.models import *

print "-------------------------- Let's test!!!!!!!! --------------------------"


# Environment Tests - Should pass everytime, if not something in the config is broken.
class SimpleTest(TestCase):
    fixtures = []

    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


# Site Test
class SiteTest(TestCase):
    fixtures = []

    def setUp(self):
        Site.objects.create(
            name="Test Site",
            login_base="test_"
        )

    def test_read_site(self):
        """
        Should read a site in the DB.
        """
        site = Site.objects.get(name="Test Site")
        # print(site._meta.get_all_field_names())
        self.assertEqual(site.login_base, "test_")


class UnautheticatedRequest(APITestCase):
    fixtures = []

    def test_require_authentication(self):
        """
        Ensure that request must be authenticated
        """
        response = self.client.get('/xos/sites/', format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SiteTestAPI(APITestCase):
    fixtures = []

    def setUp(self):
        self.site = Site.objects.create(
          name="Test Site",
          login_base="test_"
        )
        self.user = User(
            username='testuser',
            email='test@mail.org',
            password='testing',
            site=self.site,
            is_admin=True
        )
        self.user.save()
        self.client.login(email='test@mail.org', password='testing')

    def xtest_read_site_API(self):
        """
        Read a Site trough API
        """
        response = self.client.get('/xos/sites/', format='json')
        parsed = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]['login_base'], 'test_')

    def xtest_create_site_API(self):
        """
        Create a Site trough API
        """
        data = {
            'name': "Another Test Site",
            'login_base': "another_test_",
            'location': [10, 20],
            'abbreviated_name': 'test'
        }
        response = self.client.post('/xos/sites/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Site.objects.count(), 2)
        self.assertEqual(Site.objects.filter(name="Another Test Site").count(), 1)


class SliceTestAPI(APITestCase):
    fixtures = []

    def setUp(self):
        self.site = Site.objects.create(
          name="Test Site",
          login_base="test_"
        )
        self.pi = SiteRole.objects.create(role='pi')
        self.user = User(
            username='testuser',
            email='test@mail.org',
            password='testing',
            site=self.site
        )
        self.user.save()
        self.siteprivileges = SitePrivilege.objects.create(
            user=self.user,
            site=self.site,
            role=self.pi
        )
        self.serviceClass = ServiceClass.objects.create(
           name='Test Service Class'
        )
        self.client.login(email='test@mail.org', password='testing')

    # TODO
    # [x] test slice creation
    # [ ] test slice name validation - return 500
    # [x] test slice ACL
    def xtest_create_site_slice(self):
        """
        Add a slice to a given site
        """
        data = {
            'name': "test_slice",
            'site': self.site.id,
            'serviceClass': self.serviceClass.id
        }
        response = self.client.post('/xos/slices/?no_hyperlinks=1', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def xtest_validation_slice_name(self):
        """
        The slice name should start with site.login_base
        curl -H "Accept: application/json; indent=4" -u padmin@vicci.org:letmein 'http://xos:9999/xos/slices/?no_hyperlinks=1' -H "Content-Type: application/json" -X POST --data '{"name": "test", "site":"1", "serviceClass":1}'
        """
        data = {
            'name': "wrong_slice",
            'site': self.site.id,
            'serviceClass': self.serviceClass.id
        }
        response = self.client.post('/xos/slices/?no_hyperlinks=1', data, format='json')
        self.assertRaise('slice name must begin with test_')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_only_admin_can_change_creator(self):
        """
        Only an admin can change the creator of a slice
        """
        slice = Slice.objects.create(
            name="test_slice",
            site=self.site,
            serviceClass=self.serviceClass,
            creator=self.user
        )

        data = model_to_dict(slice)
        print(data)
        data['creator'] = 2

        response = self.client.put('/xos/slices/%s/?no_hyperlinks=1' % slice.id, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
