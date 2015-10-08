from basetest import BaseToscaTest

from core.models import Controller, Deployment

class ControllerTest(BaseToscaTest):
    tests = ["create_controller_minimal",
             "create_controller_maximal",
             "create_controller_nocreate",
             "destroy_controller",
             "destroy_controller_nodelete"]

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

    def create_controller_nocreate(self):
        self.assert_noobj(Controller, "testcon")
        self.execute(self.get_base_templates() +
                     self.make_nodetemplate("testcon", "tosca.nodes.Controller",
                                            reqs=[("testdep", "tosca.relationships.ControllerDeployment")],
                                            props={"no-create": True}))
        dep = self.assert_obj(Deployment, "testdep")
        self.assert_noobj(Controller, "testcon")

    def update_controller(self):
        self.assert_noobj(Controller, "testcon")
        self.execute(self.get_base_templates() +
                     self.make_nodetemplate("testcon", "tosca.nodes.Controller",
                                            reqs=[("testdep", "tosca.relationships.ControllerDeployment")]))
        dep = self.assert_obj(Deployment, "testdep")
        orig_con = self.assert_obj(Controller, "testcon",
                        backend_type="",
                        version="",
                        auth_url=None,
                        admin_user=None,
                        admin_password=None,
                        admin_tenant=None,
                        domain=None,
                        deployment=dep)
        self.execute(self.get_base_templates() +
                     self.make_nodetemplate("testcon", "tosca.nodes.Controller",
                                            reqs=[("testdep", "tosca.relationships.ControllerDeployment")],
                                            props={"version": "1.1"}))
        con = self.assert_obj(Controller, "testcon",
                        backend_type="",
                        version="1.1",
                        auth_url=None,
                        admin_user=None,
                        admin_password=None,
                        admin_tenant=None,
                        domain=None,
                        deployment=dep)
        assert(orig_con.id == con.id)

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

    def destroy_controller_nodelete(self):
        self.assert_noobj(Controller, "testcon")
        self.execute(self.get_base_templates() +
                     self.make_nodetemplate("testcon", "tosca.nodes.Controller",
                                            reqs=[("testdep", "tosca.relationships.ControllerDeployment")]))
        orig_con = self.assert_obj(Controller, "testcon")
        # NOTE: Had to specify no-delete on the deployment as well, otherwise
        # the deployment deletion would cause the controller to be deleted
        # as well. I'm thinking this is as it should be, but it's a little
        # counter-inutitive.
        self.destroy(self.make_nodetemplate("testdep", "tosca.nodes.Deployment",
                                            props={"no-delete": True}) +
                     self.make_nodetemplate("testcon", "tosca.nodes.Controller",
                                            reqs=[("testdep", "tosca.relationships.ControllerDeployment")],
                                            props={"no-delete": True}))
        con = self.assert_obj(Controller, "testcon")
        assert(orig_con.id == con.id)

if __name__ == "__main__":
    ControllerTest()


