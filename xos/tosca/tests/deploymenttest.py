from basetest import BaseToscaTest

from core.models import Deployment, Image, User, DeploymentPrivilege

class DeploymentTest(BaseToscaTest):
    tests = ["create_deployment_minimal",
             "create_deployment_maximal",
             "create_deployment_one_flavor",
             "create_deployment_two_flavors",
             "create_deployment_one_image",
             "create_deployment_two_images",
             "create_deployment_privilege",
             "create_deployment_nocreate",
             "update_deployment",
             "update_deployment_noupdate",
             "destroy_deployment",
             "destroy_deployment_nodelete"
                           ]

    def cleanup(self):
        self.try_to_delete(Deployment, name="testdep")
        self.try_to_delete(Image, name="testimg1")
        self.try_to_delete(Image, name="testimg2")
        self.try_to_delete(User, email="test@user.com")

    def create_deployment_minimal(self):
        self.assert_noobj(Deployment, "testdep")
        self.execute(self.make_nodetemplate("testdep", "tosca.nodes.Deployment"))
        dep = self.assert_obj(Deployment, "testdep",
                                   accessControl="allow all")
        assert(not dep.flavors.exists())   # there should be no flavors
        assert(not dep.images.exists()) # there should be no images


    def create_deployment_maximal(self):
        self.assert_noobj(Deployment, "testdep")
        self.execute(self.make_nodetemplate("testdep", "tosca.nodes.Deployment",
                                            props={"accessControl": "allow padmin@vicci.org"}))
        dep = self.assert_obj(Deployment, "testdep",
                                   accessControl="allow padmin@vicci.org")

    def create_deployment_one_flavor(self):
        self.assert_noobj(Deployment, "testdep")
        self.execute(self.make_nodetemplate("testdep", "tosca.nodes.Deployment",
                                            props={"accessControl": "allow padmin@vicci.org",
                                                   "flavors": "m1.small"}))
        dep = self.assert_obj(Deployment, "testdep",
                                   accessControl="allow padmin@vicci.org")

        assert( sorted([f.name for f in dep.flavors.all()]) == ["m1.small"] )

    def create_deployment_two_flavors(self):
        self.assert_noobj(Deployment, "testdep")
        self.execute(self.make_nodetemplate("testdep", "tosca.nodes.Deployment",
                                            props={"accessControl": "allow padmin@vicci.org",
                                                   "flavors": "m1.small, m1.medium"}))
        dep = self.assert_obj(Deployment, "testdep",
                                   accessControl="allow padmin@vicci.org")

        assert( sorted([f.name for f in dep.flavors.all()]) == ["m1.medium", "m1.small"] )

    def create_deployment_one_image(self):
        self.assert_noobj(Deployment, "testdep")
        self.execute(self.make_nodetemplate("testimg1", "tosca.nodes.Image") +
                     self.make_nodetemplate("testdep", "tosca.nodes.Deployment",
                                            reqs=[("testimg1", "tosca.relationships.SupportsImage")]))
        dep = self.assert_obj(Deployment, "testdep",
                                   accessControl="allow all")
        assert( sorted([f.name for f in dep.images.all()]) == ["testimg1"] )

    def create_deployment_two_images(self):
        self.assert_noobj(Deployment, "testdep")
        self.execute(self.make_nodetemplate("testimg1", "tosca.nodes.Image") +
                     self.make_nodetemplate("testimg2", "tosca.nodes.Image") +
                     self.make_nodetemplate("testdep", "tosca.nodes.Deployment",
                                            reqs=[("testimg1", "tosca.relationships.SupportsImage"),
                                                  ("testimg2", "tosca.relationships.SupportsImage")]))
        dep = self.assert_obj(Deployment, "testdep",
                                   accessControl="allow all")
        assert( sorted([f.name for f in dep.images.all()]) == ["testimg1", "testimg2"] )

    def create_deployment_privilege(self):
        self.assert_noobj(Deployment, "testdep")
        self.execute(self.make_nodetemplate("testsite", "tosca.nodes.Site") +
                     self.make_user_template() +
                     self.make_nodetemplate("testdep", "tosca.nodes.Deployment",
                                            reqs=[("test@user.com", "tosca.relationships.AdminPrivilege")]))
        dep = self.assert_obj(Deployment, "testdep")
        user = User.objects.get(email="test@user.com")

        dps = DeploymentPrivilege.objects.filter(user=user, deployment=dep)
        assert(len(dps) == 1)

    def create_deployment_nocreate(self):
        self.assert_noobj(Deployment, "testdep")
        self.execute(self.make_nodetemplate("testdep", "tosca.nodes.Deployment",
                                            props={"no-create": True}))
        self.assert_noobj(Deployment, "testdep")

    def update_deployment(self):
        self.assert_noobj(Deployment, "testdep")
        self.execute(self.make_nodetemplate("testdep", "tosca.nodes.Deployment"))
        orig_dep = self.assert_obj(Deployment, "testdep",
                                   accessControl="allow all")
        self.execute(self.make_nodetemplate("testdep", "tosca.nodes.Deployment",
                                            props={"accessControl": "allow padmin@vicci.org"}))
        dep = self.assert_obj(Deployment, "testdep",
                                   accessControl="allow padmin@vicci.org")
        assert(dep.id == orig_dep.id)

    def update_deployment_noupdate(self):
        self.assert_noobj(Deployment, "testdep")
        self.execute(self.make_nodetemplate("testdep", "tosca.nodes.Deployment"))
        orig_dep = self.assert_obj(Deployment, "testdep",
                                   accessControl="allow all")
        self.execute(self.make_nodetemplate("testdep", "tosca.nodes.Deployment",
                                            props={"accessControl": "allow padmin@vicci.org",
                                                   "no-update": True}))
        dep = self.assert_obj(Deployment, "testdep",
                                   accessControl="allow all")
        assert(dep.id == orig_dep.id)

    def destroy_deployment(self):
        self.assert_noobj(Deployment, "testdep")
        self.execute(self.make_nodetemplate("testdep", "tosca.nodes.Deployment"))
        instance = self.assert_obj(Deployment, "testdep")
        self.destroy(self.make_nodetemplate("testdep", "tosca.nodes.Deployment"))
        self.assert_noobj(Deployment, "testdep")

    def destroy_deployment_nodelete(self):
        self.assert_noobj(Deployment, "testdep")
        self.execute(self.make_nodetemplate("testdep", "tosca.nodes.Deployment"))
        instance = self.assert_obj(Deployment, "testdep")
        self.destroy(self.make_nodetemplate("testdep", "tosca.nodes.Deployment",
                                            props={"no-delete": True}))
        self.assert_obj(Deployment, "testdep")

if __name__ == "__main__":
    DeploymentTest()


