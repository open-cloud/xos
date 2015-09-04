from basetest import BaseToscaTest

from core.models import Network, Slice, NetworkTemplate, NetworkSlice

class NetworkTest(BaseToscaTest):
    tests = ["create_network_minimal",
             "create_network_maximal",
             "create_network_connected",
             "create_network_connected_two_slices",
             "update_network_labels",
             "destroy_network"]

    def cleanup(self):
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
    def private(Self):
        return NetworkTemplate.objects.get(name="Private")


    def get_base_templates(self):
        return self.make_nodetemplate("testsite", "tosca.nodes.Site") + \
               self.make_nodetemplate("testsite_slice1", "tosca.nodes.Slice", reqs=[("testsite", "tosca.relationships.MemberOfSite")]) + \
               self.make_nodetemplate("testsite_slice2", "tosca.nodes.Slice", reqs=[("testsite", "tosca.relationships.MemberOfSite")]) + \
               self.make_nodetemplate("Private", "tosca.nodes.NetworkTemplate")

    def create_network_minimal(self):
        self.assert_noobj(Network, "test_net")
        self.execute(self.get_base_templates() +
                     self.make_nodetemplate("test_net", "tosca.nodes.network.Network",
                                            reqs=[("testsite_slice1", "tosca.relationships.MemberOfSlice"),
                                                  ("Private", "tosca.relationships.UsesNetworkTemplate")]))
        net=self.assert_obj(Network, "test_net", owner=self.slice1, template=self.private)

        ns = NetworkSlice.objects.filter(slice=self.slice1, network=net)
        assert(not ns)

    def create_network_maximal(self):
        self.assert_noobj(Network, "test_net")
        self.execute(self.get_base_templates() +
                     self.make_nodetemplate("test_net", "tosca.nodes.network.Network.XOS",
                                            props={"ports": "tcp/1234, udp/5678",
                                                   "labels": "foo,bar",
                                                   "permit_all_slices": False},
                                            reqs=[("testsite_slice1", "tosca.relationships.MemberOfSlice"),
                                                  ("Private", "tosca.relationships.UsesNetworkTemplate")]))
        net=self.assert_obj(Network, "test_net",
                            owner=self.slice1,
                            template=self.private,
                            ports="tcp/1234, udp/5678",
                            labels="foo,bar",
                            permit_all_slices=False)

        ns = NetworkSlice.objects.filter(slice=self.slice1, network=net)
        assert(not ns)

    def create_network_connected(self):
        self.assert_noobj(Network, "test_net")
        self.execute(self.get_base_templates() +
                     self.make_nodetemplate("test_net", "tosca.nodes.network.Network",
                                            reqs=[("testsite_slice1", "tosca.relationships.MemberOfSlice"),
                                                  ("Private", "tosca.relationships.UsesNetworkTemplate"),
                                                  ("testsite_slice1", "tosca.relationships.ConnectsToSlice")]))

        net=self.assert_obj(Network, "test_net", owner=self.slice1, template=self.private)

        ns = NetworkSlice.objects.filter(slice=self.slice1, network=net)
        assert(ns)

    def create_network_connected_two_slices(self):
        self.assert_noobj(Network, "test_net")
        self.execute(self.get_base_templates() +
                     self.make_nodetemplate("test_net", "tosca.nodes.network.Network",
                                            reqs=[("testsite_slice1", "tosca.relationships.MemberOfSlice"),
                                                  ("Private", "tosca.relationships.UsesNetworkTemplate"),
                                                  ("testsite_slice1", "tosca.relationships.ConnectsToSlice"),
                                                  ("testsite_slice2", "tosca.relationships.ConnectsToSlice")]))

        net=self.assert_obj(Network, "test_net", owner=self.slice1, template=self.private)

        ns = NetworkSlice.objects.filter(slice=self.slice1, network=net)
        assert(ns)

        ns = NetworkSlice.objects.filter(slice=self.slice1, network=net)
        assert(ns)

    def update_network_labels(self):
        self.assert_noobj(Network, "test_net")
        self.execute(self.get_base_templates() +
                     self.make_nodetemplate("test_net", "tosca.nodes.network.Network.XOS",
                                            reqs=[("testsite_slice1", "tosca.relationships.MemberOfSlice"),
                                                  ("Private", "tosca.relationships.UsesNetworkTemplate")]))
        net=self.assert_obj(Network, "test_net", owner=self.slice1, template=self.private, labels=None)

        self.execute(self.get_base_templates() +
                     self.make_nodetemplate("test_net", "tosca.nodes.network.Network.XOS",
                                            props={"labels": "testlabel"},
                                            reqs=[("testsite_slice1", "tosca.relationships.MemberOfSlice"),
                                                  ("Private", "tosca.relationships.UsesNetworkTemplate")]))

        updated_net = self.assert_obj(Network, "test_net", owner=self.slice1, template=self.private, labels="testlabel")

        assert(net.id == updated_net.id)

    def update_network_ports(self):
        self.assert_noobj(Network, "test_net")
        self.execute(self.get_base_templates() +
                     self.make_nodetemplate("test_net", "tosca.nodes.network.Network.XOS",
                                            reqs=[("testsite_slice1", "tosca.relationships.MemberOfSlice"),
                                                  ("Private", "tosca.relationships.UsesNetworkTemplate")]))
        net=self.assert_obj(Network, "test_net", owner=self.slice1, template=self.private, labels=None, ports=None)

        self.execute(self.get_base_templates() +
                     self.make_nodetemplate("test_net", "tosca.nodes.network.Network.XOS",
                                            props={"port": "tcp/2222, udp/3333"},
                                            reqs=[("testsite_slice1", "tosca.relationships.MemberOfSlice"),
                                                  ("Private", "tosca.relationships.UsesNetworkTemplate")]))

        updated_net = self.assert_obj(Network, "test_net", owner=self.slice1, template=self.private, labels=None, ports="tcp/2222, udp/3333")

        assert(net.id == updated_net.id)

    def destroy_network(self):
        self.assert_noobj(Network, "test_net")
        self.execute(self.get_base_templates() +
                     self.make_nodetemplate("test_net", "tosca.nodes.network.Network",
                                            reqs=[("testsite_slice1", "tosca.relationships.MemberOfSlice"),
                                                  ("Private", "tosca.relationships.UsesNetworkTemplate")]))
        net=self.assert_obj(Network, "test_net", owner=self.slice1, template=self.private)

        self.destroy(self.get_base_templates() +
                     self.make_nodetemplate("test_net", "tosca.nodes.network.Network",
                                            reqs=[("testsite_slice1", "tosca.relationships.MemberOfSlice"),
                                                  ("Private", "tosca.relationships.UsesNetworkTemplate")]))

        self.assert_noobj(Network, "test_net")

if __name__ == "__main__":
    NetworkTest()


