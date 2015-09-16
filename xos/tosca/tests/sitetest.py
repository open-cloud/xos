from basetest import BaseToscaTest

from core.models import Site

class SiteTest(BaseToscaTest):
    tests = ["create_site_minimal",
             "destroy_site",
                           ]

    def cleanup(self):
        self.try_to_delete(Site, name="testsite")

    def create_site_minimal(self):
        self.assert_noobj(Site, "testsite")
        self.execute(self.make_nodetemplate("testsite", "tosca.nodes.Site"))
        instance = self.assert_obj(Site, "testsite")

    def destroy_site(self):
        self.assert_noobj(Site, "testsite")
        self.execute(self.make_nodetemplate("testsite", "tosca.nodes.Site"))
        instance = self.assert_obj(Site, "testsite")
        self.destroy(self.make_nodetemplate("testsite", "tosca.nodes.Site"))
        self.assert_noobj(Site, "testsite")

if __name__ == "__main__":
    SiteTest()


