"""
    Basic Instance Test

    1) Create a slice1
    2) Create instance1 on slice1
"""

import os
import json
import sys
import time

sys.path.append("/opt/xos")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")
from openstack.manager import OpenStackManager
from core.models import Slice, Instance, ServiceClass, Reservation, Tag, Network, User, Node, Image, Deployment, Site, NetworkTemplate, NetworkSlice

from planetstacktest import PlanetStackTest, fail_unless

class InstanceTest(PlanetStackTest):
    def __init__(self):
        PlanetStackTest.__init__(self)

    def run_instance1(self):
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

    def run(self):
        self.setup()
        try:
             self.run_instance1()
        finally:
             self.cleanup()

def main():
    InstanceTest().run()

if __name__=="__main__":
    main()
