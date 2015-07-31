import os
import sys

sys.path.append("/opt/xos")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")
import django
django.setup()
from core.models import Slice,Sliver,User,Flavor,Node,Image

class XOSNodeSelector(object):
    def __init__(self, user):
        self.user = user

    def get_allowed_nodes(self):
        # TODO: logic to get nodes that the user can use
        nodes = Node.objects.all()
        return nodes

    def get_nodes(self, quantity):
        nodes = self.get_allowed_nodes()
        # TODO: sort the nodes by some useful metric to pick the best one
        return nodes[:quantity]

