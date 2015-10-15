from basetest import BaseToscaTest

from core.models import Node, Site, Deployment, SiteDeployment

class NodeTest(BaseToscaTest):
    tests = ["create_node_minimal",
             "create_node_nocreate",
             "destroy_node",
             "destroy_node_nodelete",
                           ]

    def cleanup(self):
        self.try_to_delete(Node, name="testnode")
        self.try_to_delete(Site, name="testsite")
        self.try_to_delete(Deployment, name="testdep")

    def get_base_templates(self):
        return \
"""
    testdep:
      type: tosca.nodes.Deployment
    testcon:
      type: tosca.nodes.Controller
      requirements:
        - deployment:
            node: testdep
            relationship: tosca.relationships.ControllerDeployment
    testsite:
      type: tosca.nodes.Site
      properties:
        display_name: My Site
      requirements:
        - deployment:
             node: testdep
             relationship: tosca.relationships.SiteDeployment
             requirements:
                 - controller:
                     node: testcon
                     relationship: tosca.relationships.UsesController
"""

    def create_node_minimal(self):
        self.assert_noobj(Node, "testnode")
        self.execute(self.get_base_templates() +
                     self.make_nodetemplate("testnode", "tosca.nodes.Node",
                       reqs=[("testsite", "tosca.relationships.MemberOfSite"),
                             ("testdep", "tosca.relationships.MemberOfDeployment")]))
        node = self.assert_obj(Node, "testnode")
        assert(node.site_deployment is not None)
        assert(node.site is not None)

    def create_node_nocreate(self):
        self.assert_noobj(Node, "testnode")
        self.execute(self.get_base_templates() +
                     self.make_nodetemplate("testnode", "tosca.nodes.Node",
                       reqs=[("testsite", "tosca.relationships.MemberOfSite"),
                             ("testdep", "tosca.relationships.MemberOfDeployment")],
                       props={"no-create": True}))
        self.assert_noobj(Node, "testnode")

    def destroy_node(self):
        self.assert_noobj(Node, "testnode")
        self.execute(self.get_base_templates() +
                     self.make_nodetemplate("testnode", "tosca.nodes.Node",
                       reqs=[("testsite", "tosca.relationships.MemberOfSite"),
                             ("testdep", "tosca.relationships.MemberOfDeployment")]))
        self.assert_obj(Node, "testnode")
        self.destroy(self.get_base_templates() +
                     self.make_nodetemplate("testnode", "tosca.nodes.Node",
                       reqs=[("testsite", "tosca.relationships.MemberOfSite"),
                             ("testdep", "tosca.relationships.MemberOfDeployment")]))
        self.assert_noobj(Node, "testnode")

    def destroy_node_nodelete(self):
        self.assert_noobj(Node, "testnode")
        self.execute(self.get_base_templates() +
                     self.make_nodetemplate("testnode", "tosca.nodes.Node",
                       reqs=[("testsite", "tosca.relationships.MemberOfSite"),
                             ("testdep", "tosca.relationships.MemberOfDeployment")]))
        self.assert_obj(Node, "testnode")
        self.destroy(self.get_base_templates() +
                     self.make_nodetemplate("testnode", "tosca.nodes.Node",
                       reqs=[("testsite", "tosca.relationships.MemberOfSite"),
                             ("testdep", "tosca.relationships.MemberOfDeployment")],
                       props={"no-delete": True}))
        self.assert_obj(Node, "testnode")

if __name__ == "__main__":
    NodeTest()


