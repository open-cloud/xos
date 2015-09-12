import os
import json
import sys
import time

sys.path.append("/opt/xos")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")
from openstack.manager import OpenStackManager
from core.models import Slice, Instance, ServiceClass, Reservation, Tag, Network, User, Node, Image, Deployment, Site, NetworkTemplate, NetworkSlice

TEST_SITE_NAME = "Princeton University"
TEST_USER_EMAIL = "sbaker@planetstack.org"
TEST_IMAGE_NAME = "Fedora 16 LXC rev 1.3"
TEST_NODE_NAME = "viccidev3.cs.princeton.edu"
TEST_DEPLOYMENT_NAME = "VICCI"

def fail(msg):
    print msg
    sys.exit(-1)

def fail_unless(condition, msg):
    if not condition:
        fail(msg)

class PlanetStackTest:
    def __init__(self):
        self.objs_saved = []
        self.counter = 0

    def setup(self):
        self.manager = OpenStackManager()

        print "getting test site"
        self.testSite = Site.objects.get(name=TEST_SITE_NAME)

        print "getting test user"
        self.testUser = User.objects.get(email=TEST_USER_EMAIL)

        print "getting test image"
        self.testImage = Image.objects.get(name=TEST_IMAGE_NAME)

        print "getting test node"
        self.testNode = Node.objects.get(name=TEST_NODE_NAME)

        print "getting test deployment"
        self.testDeployment = Deployment.objects.get(name=TEST_DEPLOYMENT_NAME)

    def save_and_wait_for_enacted(self, x, nonempty_fields=[]):
        print "saving", x.__class__.__name__, str(x)
        x.save()
        self.objs_saved.append(x)
        print "   waiting for", str(x), "to be enacted"
        tStart = time.time()
        while True:
            new_x = x.__class__.objects.get(id=x.id)
            if (new_x.enacted != None) and (new_x.enacted >= new_x.updated):
                print "  ", str(x), "has been enacted"
                break
            time.sleep(5)

        if nonempty_fields:
            print "   waiting for", ", ".join(nonempty_fields), "to be nonempty"
            while True:
                new_x = x.__class__.objects.get(id=x.id)
                keep_waiting=False
                for field in nonempty_fields:
                    if not getattr(new_x, field, None):
                        keep_waiting=True
                if not keep_waiting:
                    break

        print "   saved and enacted in %d seconds" % int(time.time() - tStart)

        return new_x

    def make_slice_name(self):
        self.counter = self.counter +1
        return "test-" + str(time.time()) + "." + str(self.counter)

    def get_network_template(self,name):
        template = NetworkTemplate.objects.get(name=name)
        return template

    def cleanup(self):
        print "cleaning up"
        print "press return"
        sys.stdin.readline()
        for obj in self.objs_saved:
            try:
                 print "  deleting", str(obj)
                 obj.delete()
            except:
                 print "failed to delete", str(obj)
