from observertest import BaseObserverToscaTest

from core.models import Site, Deployment, ControllerSite

# Note that as a side effect, these tests will also create a Site

class ObserverSiteTest(BaseObserverToscaTest):
    tests = ["create_site"]
    # hide_observer_output = False # uncomment to display lots of stuff to screen

    def cleanup(self):
        # We don't want to leak rezsources, so we make sure to let the observer
        # attempt to delete these objects.
        self.try_to_delete(Site, purge=False, login_base="testsite")
        self.run_observer()
        self.try_to_delete(Site, purge=True, login_base="testsite")

    def create_site(self):
        self.assert_noobj(Site, "testsite")
        self.execute(self.make_nodetemplate(self.get_usable_deployment(), "tosca.nodes.Deployment",
                                            props={"no-delete": True}) +  \
"""
    testsite:
      type: tosca.nodes.Site
      properties:
          site_url: http://opencloud.us/
      requirements:
          - deployment:
               node: %s
               relationship: tosca.relationships.SiteDeployment
               requirements:
                   - controller:
                       node: %s
                       relationship: tosca.relationships.UsesController
""" % (self.get_usable_deployment(), self.get_usable_controller()))

        testsite = self.assert_obj(Site, "testsite")

        self.run_model_policy(save_output="/tmp/sitetest:create_site:model_policy")

        # make sure a ControllerSite object was created
        cs = ControllerSite.objects.filter(site=testsite)
        assert(len(cs) == 1)

        self.run_observer(save_output="/tmp/sitetest:create_site:observer")

        testsite = self.assert_obj(Site, "testsite")

        cs = ControllerSite.objects.filter(site=testsite)
        assert(len(cs) == 1)
        assert(cs[0].tenant_id is not None)
        assert(cs[0].tenant_id != "")

if __name__ == "__main__":
    ObserverSiteTest()

