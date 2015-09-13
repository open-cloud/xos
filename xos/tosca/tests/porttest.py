from basetest import BaseToscaTest

from core.models import Network, Slice, NetworkTemplate, NetworkSlice, Port, Instance

class PortTest(BaseToscaTest):
    tests = ["create_port_minimal",
             "create_two_ports",
             "create_four_ports",
             "add_port_after_network"]

    def cleanup(self):
        self.try_to_delete(Instance, name="test_compute1")
        self.try_to_delete(Instance, name="test_compute2")
        self.try_to_delete(Network, name="test_net")
        self.try_to_delete(Slice, name="testsite_slice1")
        self.try_to_delete(Slice, name="testsite_slice2")

    @property
    def slice1(self):
        return Slice.objects.get(name="testsite_slice1")

    @property
    def slice2(self):
        return Slice.objects.get(name="testsite_slice2")

    @property
    def private(self):
        return NetworkTemplate.objects.get(name="Private")

    @property
    def test_slice1_1(self):
        return Instance.objects.get(name="test_slice1-1")

    @property
    def test_slice1_2(self):
        return Instance.objects.get(name="test_slice1-2")

    @property
    def test_slice2_1(self):
        return Instance.objects.get(name="test_slice2-1")

    @property
    def test_slice2_2(self):
        return Instance.objects.get(name="test_slice2-2")

    def get_base_templates(self):
        return self.make_nodetemplate("testsite", "tosca.nodes.Site") + \
               self.make_nodetemplate("testsite_slice1", "tosca.nodes.Slice", reqs=[("testsite", "tosca.relationships.MemberOfSite")]) + \
               self.make_nodetemplate("testsite_slice2", "tosca.nodes.Slice", reqs=[("testsite", "tosca.relationships.MemberOfSite")]) + \
               self.make_nodetemplate("Private", "tosca.nodes.NetworkTemplate") + \
               self.make_compute("testsite_slice1", "test_slice1-1") + \
               self.make_compute("testsite_slice1", "test_slice1-2") +\
               self.make_compute("testsite_slice2", "test_slice2-1") + \
               self.make_compute("testsite_slice2", "test_slice2-2")

    def create_port_minimal(self):
        self.assert_noobj(Network, "test_net")
        self.execute(self.get_base_templates() +
                     self.make_nodetemplate("test_net", "tosca.nodes.network.Network",
                                            reqs=[("testsite_slice1", "tosca.relationships.MemberOfSlice"),
                                                  ("Private", "tosca.relationships.UsesNetworkTemplate")]) +
                     self.make_nodetemplate("test_port", "tosca.nodes.network.Port",
                                            reqs=[("test_net", "tosca.relationships.network.LinksTo"),
                                                  ("test_slice1-1", "tosca.relationships.network.BindsTo")]))

        net=self.assert_obj(Network, "test_net")

        port=Port.objects.filter(network=net, instance=self.test_slice1_1)
        assert(len(port)==1)
        port=port[0]

    def create_two_ports(self):
        self.assert_noobj(Network, "test_net")
        self.execute(self.get_base_templates() +
                     self.make_nodetemplate("test_net", "tosca.nodes.network.Network",
                                            reqs=[("testsite_slice1", "tosca.relationships.MemberOfSlice"),
                                                  ("Private", "tosca.relationships.UsesNetworkTemplate")]) +
                     self.make_nodetemplate("test_port1", "tosca.nodes.network.Port",
                                            reqs=[("test_net", "tosca.relationships.network.LinksTo"),
                                                  ("test_slice1-1", "tosca.relationships.network.BindsTo")]) +
                     self.make_nodetemplate("test_port2", "tosca.nodes.network.Port",
                                            reqs=[("test_net", "tosca.relationships.network.LinksTo"),
                                                  ("test_slice1-2", "tosca.relationships.network.BindsTo")]))

        net=self.assert_obj(Network, "test_net")

        port=Port.objects.filter(network=net, instance=self.test_slice1_1)
        assert(len(port)==1)
        port=port[0]

        port=Port.objects.filter(network=net, instance=self.test_slice1_2)
        assert(len(port)==1)
        port=port[0]

    def create_four_ports(self):
        self.assert_noobj(Network, "test_net")
        self.execute(self.get_base_templates() +
                     self.make_nodetemplate("test_net", "tosca.nodes.network.Network",
                                            reqs=[("testsite_slice1", "tosca.relationships.MemberOfSlice"),
                                                  ("Private", "tosca.relationships.UsesNetworkTemplate")]) +
                     self.make_nodetemplate("test_port1", "tosca.nodes.network.Port",
                                            reqs=[("test_net", "tosca.relationships.network.LinksTo"),
                                                  ("test_slice1-1", "tosca.relationships.network.BindsTo")]) +
                     self.make_nodetemplate("test_port2", "tosca.nodes.network.Port",
                                            reqs=[("test_net", "tosca.relationships.network.LinksTo"),
                                                  ("test_slice1-2", "tosca.relationships.network.BindsTo")]) +
                     self.make_nodetemplate("test_port3", "tosca.nodes.network.Port",
                                            reqs=[("test_net", "tosca.relationships.network.LinksTo"),
                                                  ("test_slice2-1", "tosca.relationships.network.BindsTo")]) +
                     self.make_nodetemplate("test_port4", "tosca.nodes.network.Port",
                                            reqs=[("test_net", "tosca.relationships.network.LinksTo"),
                                                  ("test_slice2-2", "tosca.relationships.network.BindsTo")]))

        net=self.assert_obj(Network, "test_net")

        port=Port.objects.filter(network=net, instance=self.test_slice1_1)
        assert(len(port)==1)
        port=port[0]

        port=Port.objects.filter(network=net, instance=self.test_slice1_2)
        assert(len(port)==1)
        port=port[0]

        port=Port.objects.filter(network=net, instance=self.test_slice2_2)
        assert(len(port)==1)
        port=port[0]

        port=Port.objects.filter(network=net, instance=self.test_slice2_2)
        assert(len(port)==1)
        port=port[0]

    def add_port_after_network(self):
        self.assert_noobj(Network, "test_net")
        self.execute(self.get_base_templates() +
                     self.make_nodetemplate("test_net", "tosca.nodes.network.Network",
                                            reqs=[("testsite_slice1", "tosca.relationships.MemberOfSlice"),
                                                  ("Private", "tosca.relationships.UsesNetworkTemplate")]))


        orig_net=self.assert_obj(Network, "test_net")

        self.execute(self.get_base_templates() +
                     self.make_nodetemplate("test_net", "tosca.nodes.network.Network",
                                            reqs=[("testsite_slice1", "tosca.relationships.MemberOfSlice"),
                                                  ("Private", "tosca.relationships.UsesNetworkTemplate")]) +
                     self.make_nodetemplate("test_port1", "tosca.nodes.network.Port",
                                            reqs=[("test_net", "tosca.relationships.network.LinksTo"),
                                                  ("test_slice1-1", "tosca.relationships.network.BindsTo")]))

        net=self.assert_obj(Network, "test_net")

        assert(orig_net.id == net.id)

        port=Port.objects.filter(network=net, instance=self.test_slice1_1)
        assert(len(port)==1)
        port=port[0]


if __name__ == "__main__":
    PortTest()


