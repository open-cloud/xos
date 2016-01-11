#!/usr/bin/env python
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
import json

from core.models import *

print "-------------------------- Let's test!!!!!!!! --------------------------"


# Environment Tests - Should pass everytime, if not something in the config is broken.
class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


# Site Test
class SiteTest(TestCase):
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
    def test_require_authentication(self):
        """
        Ensure that request must be authenticated
        """
        response = self.client.get('/xos/sites/', format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SiteTestAPI(APITestCase):
    def setUp(self):
        self.site = Site.objects.create(
          name="Test Site",
          login_base="test_"
        )
        self.user = User(
            username='testuser',
            email='test@mail.org',
            password='testing',
            site=self.site
        )
        self.user.save()
        self.client.login(email='test@mail.org', password='testing')

    def test_read_site_API(self):
        """
        Read a Site trough API
        """
        response = self.client.get('/xos/sites/', format='json')
        parsed = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]['login_base'], 'test_')

    def test_create_site_API(self):
        """
        Create a Site trough API
        """
        data = {
            'name': "Another Test Site",
            'login_base': "another_test_"
        }
        response = self.client.post('/xos/sites/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Site.objects.count(), 2)
        self.assertEqual(Site.objects.get(name="Another Test Site").count(), 1)

    def tearDown(self):
        Site.objects.all().delete()
        User.objects.all().delete()
