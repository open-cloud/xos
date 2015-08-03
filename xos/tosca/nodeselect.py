import os
import sys

from core.models import Slice,Sliver,User,Flavor,Node,Image

class XOSNodeSelector(object):
    def __init__(self, user, mem_size=None, num_cpus=None, disk_size=None):
        self.user = user

    def get_allowed_nodes(self):
        # TODO: logic to get nodes that the user can use
        nodes = Node.objects.all()
        return nodes

    def get_nodes(self, quantity):
        nodes = self.get_allowed_nodes()
        # TODO: sort the nodes by some useful metric to pick the best one
        return nodes[:quantity]

