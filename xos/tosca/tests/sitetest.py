from basetest import BaseToscaTest

from core.models import Site, SitePrivilege, User

class SiteTest(BaseToscaTest):
    tests = ["create_site_minimal",
             "create_site_privilege_tech",
             "create_site_privilege_admin",
             "create_site_privilege_pi",
             "destroy_site",
                           ]

    def cleanup(self):
        self.try_to_delete(Site, name="testsite")

    def create_site_minimal(self):
        self.assert_noobj(Site, "testsite")
        self.execute(self.make_nodetemplate("testsite", "tosca.nodes.Site"))
        site = self.assert_obj(Site, "testsite")

    def create_site_privilege_tech(self):
        self.assert_noobj(Site, "testsite")
        self.execute(self.make_nodetemplate("testsite", "tosca.nodes.Site") +
                     self.make_nodetemplate("test@user.com", "tosca.nodes.User",
                         props = {"firstname": "test", "lastname": "user", "password": "letmein"},
                         reqs = [("testsite", "tosca.relationships.MemberOfSite"),
                                 ("testsite", "tosca.relationships.TechPrivilege")]))
        site = self.assert_obj(Site, "testsite")
        user = User.objects.get(email="test@user.com")

        sps = SitePrivilege.objects.filter(site=site, user=user)
        assert(len(sps) == 1)
        assert(sps[0].role.role == "tech")

    def create_site_privilege_admin(self):
        self.assert_noobj(Site, "testsite")
        self.execute(self.make_nodetemplate("testsite", "tosca.nodes.Site") +
                     self.make_nodetemplate("test@user.com", "tosca.nodes.User",
                         props = {"firstname": "test", "lastname": "user", "password": "letmein"},
                         reqs = [("testsite", "tosca.relationships.MemberOfSite"),
                                 ("testsite", "tosca.relationships.AdminPrivilege")]))
        site = self.assert_obj(Site, "testsite")
        user = User.objects.get(email="test@user.com")

        sps = SitePrivilege.objects.filter(site=site, user=user)
        assert(len(sps) == 1)
        assert(sps[0].role.role == "admin")

    def create_site_privilege_pi(self):
        self.assert_noobj(Site, "testsite")
        self.execute(self.make_nodetemplate("testsite", "tosca.nodes.Site") +
                     self.make_nodetemplate("test@user.com", "tosca.nodes.User",
                         props = {"firstname": "test", "lastname": "user", "password": "letmein"},
                         reqs = [("testsite", "tosca.relationships.MemberOfSite"),
                                 ("testsite", "tosca.relationships.PIPrivilege")]))
        site = self.assert_obj(Site, "testsite")
        user = User.objects.get(email="test@user.com")

        sps = SitePrivilege.objects.filter(site=site, user=user)
        assert(len(sps) == 1)
        assert(sps[0].role.role == "pi")

    def destroy_site(self):
        self.assert_noobj(Site, "testsite")
        self.execute(self.make_nodetemplate("testsite", "tosca.nodes.Site"))
        site = self.assert_obj(Site, "testsite")
        self.destroy(self.make_nodetemplate("testsite", "tosca.nodes.Site"))
        self.assert_noobj(Site, "testsite")

if __name__ == "__main__":
    SiteTest()


