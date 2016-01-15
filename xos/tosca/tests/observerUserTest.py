from observertest import BaseObserverToscaTest

from core.models import Site, Deployment, User, ControllerUser

# Note that as a side effect, these tests will also create a Site

class ObserverUserTest(BaseObserverToscaTest):
    tests = ["create_user"]
    # hide_observer_output = False # uncomment to display lots of stuff to screen

    def cleanup(self):
        # We don't want to leak resources, so we make sure to let the observer
        # attempt to delete these objects.
        self.try_to_delete(User, purge=False, email="johndoe@foo.bar")
        self.try_to_delete(Site, purge=False, login_base="testsite")
        self.run_observer()
        self.try_to_delete(User, purge=True, email="johndoe@foo.bar")
        self.try_to_delete(Site, purge=True, login_base="testsite")

    def assert_nouser(self, email):
        assert(not User.objects.filter(email=email))

    def assert_user(self, email, **kwargs):
        obj = User.objects.get(email=email)
        assert(obj)
        for (k,v) in kwargs.items():
            if (getattr(obj,k,None) != v):
                print "Object %s property '%s' is '%s' and should be '%s'" % (obj, k, getattr(obj,k,None), v)
                assert(False)
        return obj

    def create_user(self):
        self.assert_noobj(Site, "testsite")
        self.assert_nouser("johndoe@foo.bar")
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
    johndoe@foo.bar:
      type: tosca.nodes.User
      properties:
          password: letmein
          firstname: john
          lastname: doe
      requirements:
          - site:
              node: testsite
              relationship: tosca.relationships.MemberOfSite
""" % (self.get_usable_deployment(), self.get_usable_controller()))

        testsite = self.assert_obj(Site, "testsite")
        testuser = self.assert_user("johndoe@foo.bar")

        self.run_model_policy(save_output="/tmp/usertest:create_user:model_policy")

        # make sure a ControllerSite object was created
        cu = ControllerUser.objects.filter(user=testuser)
        assert(len(cu) == 1)

        self.run_observer(save_output="/tmp/usertest:create_user:observer")

        testuser = self.assert_user("johndoe@foo.bar")

        cu = ControllerUser.objects.filter(user=testuser)
        assert(len(cu) == 1)
        assert(cu[0].kuser_id is not None)
        assert(cu[0].kuser_id != "")

if __name__ == "__main__":
    ObserverUserTest()

