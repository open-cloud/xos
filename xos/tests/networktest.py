"""
    Network Data Model Test

    1) Create a slice1
    2) Create instance1 on slice1
    3) Verify one quantum network created for instance1
    4) Create a private network, network1
    5) Connect network1 to slice1
    6) Create instance1_2 on slice1
    7) Verify two quantum networks created for instance1_2
"""

import os
import json
import sys
import time

sys.path.append("/opt/xos")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")
from openstack.manager import OpenStackManager
from core.models import Slice, Instance, ServiceClass, Reservation, Tag, Network, User, Node, Image, Deployment, Site, NetworkTemplate, NetworkSlice

from planetstacktest import PlanetStackTest, fail_unless, fail

class NetworkTest(PlanetStackTest):
    def __init__(self):
        PlanetStackTest.__init__(self)

    def wait_for_ports(self, instance, count=1, max_time=120):
        print "waiting for %d ports on %s" % (count, str(instance))
        while max_time>0:
            ports = self.manager.driver.shell.quantum.list_ports(device_id=instance.instance_id)["ports"]
            if len(ports)==count:
                return ports

            fail_unless(len(ports)<=count, "too many ports")

            time.sleep(10)
            max_time = max_time - 10

        fail("timed out while waiting for port creation")

    def ports_to_networks(self, ports):
        networks = []
        for port in ports:
            port_networks = networks + self.manager.driver.shell.quantum.list_networks(id=port["network_id"])["networks"]
            for network in port_networks:
                if not (network in networks):
                    networks.append(network)
        return networks

    def ports_to_network_names(self, ports):
        network_names = []
        for network in self.ports_to_networks(ports):
             network_names.append(network["name"])
        return network_names

    def verify_network_names(self, ports, network_names):
        port_network_names = sorted(self.ports_to_network_names(ports))
        network_names = sorted(network_names)
        fail_unless(port_network_names == network_names, "mismatched network names: %s != %s" % (str(port_network_names), str(network_names)))
        print "   verified network ports to", ",".join(port_network_names)

    def test_slice1(self):
        slice1Name = self.make_slice_name()
        slice1 = Slice(name = slice1Name,
                       omf_friendly=True,
                       site=self.testSite,
                       creator=self.testUser)
        slice1=self.save_and_wait_for_enacted(slice1, nonempty_fields=["tenant_id"])

        instance1 = Instance(image = self.testImage,
                         creator=self.testUser,
                         slice=slice1,
                         node=self.testNode,
                         deploymentNetwork=self.testDeployment)
        instance1=self.save_and_wait_for_enacted(instance1, nonempty_fields=["instance_id", "ip"])

        # instance1 should have only one port, its private network
        ports = self.wait_for_ports(instance1, count=1)
        self.verify_network_names(ports, [slice1.name])

        network1 = Network(name = slice1Name + "-pvt",
                           template = self.get_network_template("private"),
                           owner = slice1)
        network1=self.save_and_wait_for_enacted(network1, nonempty_fields=["network_id", "subnet_id", "router_id", "subnet"])

        network1_slice1 = NetworkSlice(network=network1, slice=slice1)
        network1_slice1.save() # does not need to be enacted

        instance1_2 = Instance(image = self.testImage,
                         creator=self.testUser,
                         slice=slice1,
                         node=self.testNode,
                         deploymentNetwork=self.testDeployment)
        instance1_2=self.save_and_wait_for_enacted(instance1_2, nonempty_fields=["instance_id", "ip"])

        ports = self.wait_for_ports(instance1_2, count=2)
        self.verify_network_names(ports, [slice1.name, network1.name])

        self.slice1 = slice1
        self.network1 = network1

    def test_slice2(self):
        slice2Name = self.make_slice_name()
        slice2 = Slice(name = slice2Name,
                       omf_friendly=True,
                       site=self.testSite,
                       creator=self.testUser)
        slice2=self.save_and_wait_for_enacted(slice2, nonempty_fields=["tenant_id"])

        network2 = Network(name = slice2Name + "-pvt",
                           template = self.get_network_template("private"),
                           owner = slice2)
        network2=self.save_and_wait_for_enacted(network2, nonempty_fields=["network_id", "subnet_id", "router_id", "subnet"])

        network2_slice2 = NetworkSlice(network=network2, slice=slice2)
        network2_slice2.save() # does not need to be enacted

        instance2_1 = Instance(image = self.testImage,
                         creator=self.testUser,
                         slice=slice2,
                         node=self.testNode,
                         deploymentNetwork=self.testDeployment)
        instance2_1=self.save_and_wait_for_enacted(instance2_1, nonempty_fields=["instance_id", "ip"])

        ports = self.wait_for_ports(instance2_1, count=2)
        self.verify_network_names(ports, [slice2.name, network2.name])

        self.slice2 = slice2
        self.network2 = network2

    def test_shared_private_net(self):
        # connect network2 to slice1
        self.network2.permittedSlices.add(self.slice1)
        network2_slice1 = NetworkSlice(network=self.network2, slice=self.slice1)
        network2_slice1.save()

        instance1_3 = Instance(image = self.testImage,
                         creator=self.testUser,
                         slice=self.slice1,
                         node=self.testNode,
                         deploymentNetwork=self.testDeployment)
        instance1_3=self.save_and_wait_for_enacted(instance1_3, nonempty_fields=["instance_id", "ip"])

        ports = self.wait_for_ports(instance1_3, count=3)
        self.verify_network_names(ports, [self.slice1.name, self.network1.name, self.network2.name])

    def test_nat_net(self):
        slice3Name = self.make_slice_name()
        slice3 = Slice(name = slice3Name,
                       omf_friendly=True,
                       site=self.testSite,
                       creator=self.testUser)
        slice3=self.save_and_wait_for_enacted(slice3, nonempty_fields=["tenant_id"])

        network3 = Network(name = slice3Name + "-nat",
                           template = self.get_network_template("private-nat"),
                           owner = slice3)
        # note that router_id will not be filled in for nat-net, since nat-net has no routers
        network3=self.save_and_wait_for_enacted(network3, nonempty_fields=["network_id", "subnet_id", "subnet"])

        network3_slice3 = NetworkSlice(network=network3, slice=slice3)
        network3_slice3.save() # does not need to be enacted

        instance3_1 = Instance(image = self.testImage,
                         creator=self.testUser,
                         slice=slice3,
                         node=self.testNode,
                         deploymentNetwork=self.testDeployment)
        instance3_1=self.save_and_wait_for_enacted(instance3_1, nonempty_fields=["instance_id", "ip"])

        ports = self.wait_for_ports(instance3_1, count=2)
        self.verify_network_names(ports, [slice3.name, "nat-net"])

    def run(self):
        self.setup()
        try:
             self.test_slice1()
             self.test_slice2()
             self.test_shared_private_net()
             self.test_nat_net()
             print "SUCCESS"
        finally:
             self.cleanup()

def main():
    NetworkTest().run()

if __name__=="__main__":
    main()



