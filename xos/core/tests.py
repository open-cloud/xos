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
        parsed = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(parsed['detail']['specific_error'], "slice name must begin with test_")

    def xtest_only_admin_can_change_creator(self):
        """
        Only an admin can change the creator of a slice
        """
        slice = Slice.objects.create(
            name="test_slice",
            site=self.site,
            serviceClass=self.serviceClass,
            creator=self.user
        )

        user2 = User(
            username='another_testuser',
            email='another_test@mail.org',
            password='testing',
            site=self.site
        )
        user2.save()

        data = model_to_dict(slice)
        data['creator'] = user2.id

        response = self.client.put('/xos/slices/%s/?no_hyperlinks=1' % slice.id, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        parsed = json.loads(response.content)
        self.assertEqual(parsed['detail']['specific_error'], "Insufficient privileges to change slice creator")

class ServiceTestAPI(APITestCase):
    fixtures = []

    def setUp(self):
        self.site = Site.objects.create(
            name="Test Site",
            login_base="test_"
        )
        self.admin = User(
            username='testadmin',
            email='admin@mail.org',
            password='testing',
            site=self.site,
            is_admin=True
        )
        self.admin.save()

        self.user = User(
            username='testuser',
            email='user@mail.org',
            password='testing',
            site=self.site
        )
        self.user.save()

        self.service1 = Service.objects.create(
            name="fakeService1",
            versionNumber="1.0.0",
            published=True,
            enabled=True
        )

        self.service2 = Service.objects.create(
            name="fakeService1",
            versionNumber="1.0.0",
            published=True,
            enabled=True
        )

        self.service_role = ServiceRole.objects.create(role='admin')

        self.service_privileges = ServicePrivilege.objects.create(
            user=self.user,
            service=self.service2,
            role=self.service_role
        )

    # TODO
    # [x] admin view all service
    # [ ] user view only service2
    # [x] admin view a specific service service
    # [ ] user view can't view a specific service
    # [ ] user update service2
    # [ ] usercan NOT update service2
    # [x] admin update service1
    def xtest_admin_read_all_service(self):
        """
        Admin should read all the services
        """
        self.client.login(email='admin@mail.org', password='testing')
        response = self.client.get('/xos/services/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json.loads(response.content)), 2)

    # need to understand how slices are related
    def xtest_user_read_all_service(self):
        """
        User should read only service for which have privileges
        """
        self.client.login(email='user@mail.org', password='testing')
        response = self.client.get('/xos/services/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json.loads(response.content)), 1)

    def xtest_admin_read_one_service(self):
        """
        Read a given service
        """
        self.client.login(email='admin@mail.org', password='testing')
        response = self.client.get('/xos/services/%s/' % self.service1.id, format='json')
        parsed = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(parsed['name'], self.service1.name)

    def test_admin_update_service(self):
        """
        Update a given service
        """
        data = model_to_dict(self.service1)
        data['name'] = "newName"

        self.client.login(email='admin@mail.org', password='testing')
        response = self.client.put('/xos/services/%s/' % self.service1.id, data, format='json')
        parsed = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        model = Service.objects.get(id=self.service1.id)
        self.assertEqual(model.name, data['name'])