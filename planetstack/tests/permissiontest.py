import unittest
from core.models import *

class TestPermission(unittest.TestCase):
    
    def setUp(self):
        self.test_objects = []
        # deployment
        self.deployment = Deployment(name='TestDeployment')
        self.deployment.save()
        self.test_objects.append(self.deployment)
        # site
        self.site = Site(name='TestSite')
        self.site.save()
        self.test_objects.append(self.site)
        # site deployment
        self.site_deployment = SiteDeployment(site=self.site, deployment=self.deployment)
        self.site_deployment.save()
        self.test_objects.append(self.site_deployment)
        # node
        self.node = Node(name='TestNode', site_deployment=self.site_deployment)
        self.node.save()
        self.test_objects.append(self.node)
        # slice
        self.slice = Slice(name='TestSlice', site=self.site)
        self.slice.save()
        self.test_objects.appen(slice.slice)
        # admin user
        self.user_admin = User(email='user_admin@test.com', first_name='Test', last_name='Test', is_admin=True)
        self.user_admin.site = self.site
        self.user_admin.save()
        self.test_objects.append(self.user_admin)
        # read only user
        self.user_read_only = User(email='user_read_only@test.com', first_name='Test', last_name='Test')
        self.user_read_only.site = self.site
        self.user_read_only.save()
        self.test_objects.append(self.user_read_only)
        # default user
        self.user_default = User(email='user_default@test.com', first_name='Test', last_name='Test')
        self.user_default.site = self.site 
        self.user_default.save()
        self.test_objects.append(self.user_default)

        # deployment admin 
        self.user_deployment_admin = User(email='user_deployment_admin@test.com', first_name='Test', last_name='Test')
        self.user_deployment_admin.site = self.site
        self.user_deployment_admin.save()
        self.test_objects.append(self.user_deployment_admin)
        deployment_privilege = DeploymentPrivilege(
            user=self.user_deployment_admin,
            deployment=self.deployment,
            role='admin')
        deployment_privilege.save()
        self.test_objects.append(deployment_privilege)
        # site admin
        self.user_site_admin = User(email='user_site_admin@test.com', first_name='Test', last_name='Test')
        self.user_site_admin = self.site
        self.user_site_admin.save()
        self.test_objects.append(self.user_site_admin)
        site_admin_privilege = SitePrivilege(
            user = self.user_site_admin,
            site=self.site,
            role='admin')
        site_admin_privilege.save()
        self.test_objects.append(site_admin_privilege)
        # site pi
        self.user_site_pi = User(email='user_site_pi@test.com', first_name='Test', last_name='Test')
        self.user_site_pi = self.site
        self.user_site_pi.save()
        self.test_objects.append(self.user_site_pi)
        site_pi_privilege = SitePrivilege(
            user = self.user_site_pi,
            site=self.site,
            role='pi')
        site_pi_privilege.save()
        self.test_objects.append(site_pi_privilege)
        # site tech
        self.user_site_tech = User(email='user_site_tech@test.com', first_name='Test', last_name='Test')
        self.user_site_tech = self.site
        self.user_site_tech.save()
        self.test_objects.append(self.user_site_tech)
        site_tech_privilege = SitePrivilege(
            user = self.user_site_tech,
            site=self.site,
            role='tech')
        site_tech_privilege.save()
        self.test_objects.append(site_tech_privilege)
        # slice admin
        self.user_slice_admin = User(email='user_slice_admin@test.com', first_name='Test', last_name='Test')
        self.user_slice_admin = self.site
        self.user_slice_admin.save()
        self.test_objects.append(self.user_slice_admin)
        slice_admin_privilege = SlicePrivilege(
            user = self.user_slice_admin,
            slice = self.slice,
            role='admin')
        slice_admin_privilege.save()
        self.test_objects.append(slice_admin_privilege)
        # slice access 
        self.user_slice_access = User(email='user_slice_access@test.com', first_name='Test', last_name='Test')
        self.user_slice_access = self.site 
        self.user_slice_access.save()
        self.test_objects.append(self.user_slice_access)
        slice_access_privilege = SlicePrivilege(
            user = self.user_slice_access,
            slice = self.slice,
            role='access')
        slice_access_privilege.save()
        self.test_objects.append(slice_access_privilege)


    def test_deployment(self):
        for user in [self.user_admin, self.user_deployment_admin]:
            self.assertEqual(
                self.deployment.save_by_user(user), None)
        for user in [self.user_read_only, self.user_default, self.user_site_admin,
                     self.user_site_pi, self.user_site_tech, self.user_slice_admin,
                     self.user_slice_access]:
            self.assertRaises(
                PermissionDenied, 
                self.deployment.save_by_user(user,))

    def test_site(self):
        for user in [self.user_admin, self.user_site_admin, self.user_site_pi]:
            self.assertEqual(
                self.site.save_by_user(user), None)
        for user in [self.user_read_only, self.user_default, self.user_deployment_admin,
                     self.user_site_tech, self.user_slice_admin, self.user_slice_access]:
            self.assertRaises(
                PermissionDenied,
                self.site.save_by_user(user,))
    
    def test_node(self):
        for user in [self.user_admin, self.user_site_admin, self.user_site_tech]:
            self.assertEqual(self.node.save_by_user(user), None)
        for user in [self.user_read_only, self.user_default, self.user_deployment_admin,
                     self.user_site_pi, self.user_slice_admin, self.user_slice_access]:
            self.assertRaises(
                PermissionDenied,
                self.node.save_by_user(user,))                 
                                       
    def test_slice(self):
        for user in [self.user_admin, self.user_site_admin, self.user_site_pi, 
                     self.user_slice_admin]:
            self.assertEqual(
                self.slice.save_by_user(user), None)
        for user in [self.user_read_only, self.user_default, self.user_deployment_admin,
                     self.user_site_tech, self.user_slice_access]:
            self.assertRaises(
                PermissionDenied,
                self.slice.save_by_user(user,))
            
    def test_user(self):
        for user in [self.user_admin, self.user_site_admin, self.user_deployment_admin,
                     self.user_site_pi, self.user_default]:
            self.assertEqual(
                self.user_default.save_by_user(user), None)
        for user in [self.user_read_only, self.user_deployment_admin, 
                     self.user_site_tech, self.user_slice_admin, self.user_slice_access]:
            self.assertRaises(
                PermissionDenied,
                self.user_default.save_by_user(user,))                    
                                 
         
    def tearDown(self):
        for obj in self.test_objects:
            obj.delete()       
    
if __name__ == '__main__':
    unittest.main()     
