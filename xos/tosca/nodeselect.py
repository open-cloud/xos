import os
import sys

from core.models import Slice,Instance,User,Flavor,Node,Image

class XOSNodeSelector(object):
    def __init__(self, user, mem_size=None, num_cpus=None, disk_size=None, hostname = None):
        self.user = user
        self.hostname = None

    def get_allowed_nodes(self):
        # TODO: logic to get nodes that the user can use
        nodes = Node.objects.all()

        if self.hostname:
            nodes = nodes.filter(name = self.hostname)

        return nodes

    def get_nodes(self, quantity):
        nodes = self.get_allowed_nodes()
        # TODO: filter out any nonfunctional nodes
        # sort by fewest number of instances
        nodes = sorted(nodes, key=lambda node: node.instances.all().count())
        return nodes[:quantity]

