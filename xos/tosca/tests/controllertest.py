from basetest import BaseToscaTest

from core.models import Controller, Deployment

class ControllerTest(BaseToscaTest):
    tests = ["create_controller_minimal",
             "create_controller_maximal",
             "destroy_controller"]

    def cleanup(self):
        self.try_to_delete(Controller, name="testcon")
        self.try_to_delete(Deployment, name="testdep")

    def get_base_templates(self):
        return self.make_nodetemplate("testdep", "tosca.nodes.Deployment")

    def create_controller_minimal(self):
        self.assert_noobj(Controller, "testcon")
        self.execute(self.get_base_templates() +
                     self.make_nodetemplate("testcon", "tosca.nodes.Controller",
                                            reqs=[("testdep", "tosca.relationships.ControllerDeployment")]))
        dep = self.assert_obj(Deployment, "testdep")
        self.assert_obj(Controller, "testcon",
                        backend_type="",
                        version="",
                        auth_url=None,
                        admin_user=None,
                        admin_password=None,
                        admin_tenant=None,
                        domain=None,
                        deployment=dep)

    def create_controller_maximal(self):
        self.assert_noobj(Controller, "testcon")
        self.execute(self.get_base_templates() +
                     self.make_nodetemplate("testcon", "tosca.nodes.Controller",
                                            reqs=[("testdep", "tosca.relationships.ControllerDeployment")],
                                            props={"backend_type": "openstack",
                                                   "version": "v1.23.4",
                                                   "auth_url": "http://foo.com/",
                                                   "admin_user": "johndoe",
                                                   "admin_password": "letmeout",
                                                   "admin_tenant": "12345678",
                                                   "domain": "mydomain"}))
        dep = self.assert_obj(Deployment, "testdep")
        self.assert_obj(Controller, "testcon",
                        backend_type="openstack",
                        version="v1.23.4",
                        auth_url="http://foo.com/",
                        admin_user="johndoe",
                        admin_password="letmeout",
                        admin_tenant="12345678",
                        domain="mydomain",
                        deployment=dep)

    def destroy_controller(self):
        self.assert_noobj(Controller, "testcon")
        self.execute(self.get_base_templates() +
                     self.make_nodetemplate("testcon", "tosca.nodes.Controller",
                                            reqs=[("testdep", "tosca.relationships.ControllerDeployment")]))
        self.assert_obj(Controller, "testcon")
        self.destroy(self.get_base_templates() +
                     self.make_nodetemplate("testcon", "tosca.nodes.Controller",
                                            reqs=[("testdep", "tosca.relationships.ControllerDeployment")]))
        self.assert_noobj(Controller, "testcon")

if __name__ == "__main__":
    ControllerTest()


