from basetest import BaseToscaTest

from core.models import Deployment

class DeploymentTest(BaseToscaTest):
    tests = ["create_deployment_minimal",
             "destroy_deployment",
                           ]

    def cleanup(self):
        self.try_to_delete(Deployment, name="testdep")

    def create_deployment_minimal(self):
        self.assert_noobj(Deployment, "testdep")
        self.execute(self.make_nodetemplate("testdep", "tosca.nodes.Deployment"))
        instance = self.assert_obj(Deployment, "testdep")

    def destroy_deployment(self):
        self.assert_noobj(Deployment, "testdep")
        self.execute(self.make_nodetemplate("testdep", "tosca.nodes.Deployment"))
        instance = self.assert_obj(Deployment, "testdep")
        self.destroy(self.make_nodetemplate("testdep", "tosca.nodes.Deployment"))
        self.assert_noobj(Deployment, "testdep")

if __name__ == "__main__":
    DeploymentTest()


