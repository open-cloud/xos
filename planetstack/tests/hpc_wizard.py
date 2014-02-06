import datetime
import os
import operator
import socket
import pytz
import json
import random
import sys
import time

#sys.path.append("/opt/planetstack")
sys.path.append("/home/smbaker/projects/vicci/plstackapi/planetstack")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "planetstack.settings")
from core.models import Slice, Sliver, ServiceClass, Reservation, Tag, Network, User, Node, Image, Deployment, Site, NetworkTemplate, NetworkSlice, Service
from hpc.models import HpcService, ServiceProvider, ContentProvider, OriginServer, CDNPrefix, HpcService

def format_float(x):
    try:
        return "%10.5f" % x
    except:
        return str(x)

class HpcWizard:
    def __init__(self):
        self.hpcService = HpcService.objects.get()

    def get_hpc_slices(self):
        slices = self.hpcService.slices.all()
        return slices

    def get_hpc_slivers(self):
        slivers = []
        for slice in self.get_hpc_slices():
            for sliver in slice.slivers.all():
                slivers.append(sliver)
        return slivers

    def fill_site_nodes(self, site, hpc_slivers=None):
        if hpc_slivers is None:
            hpc_slivers = self.get_hpc_slivers()

        site.availNodes = []
        site.hpcNodes = []
        for node in site.nodes.all():
            has_hpc = False
            for sliver in node.slivers.all():
                if sliver in hpc_slivers:
                    has_hpc = True
            if has_hpc:
                site.hpcNodes.append(node)
            else:
                site.availNodes.append(node)

    def get_sites(self):
        sites = list(Site.objects.all())

        for site in sites:
            self.fill_site_nodes(site, self.get_hpc_slivers())

        return sites

    def get_site(self, site_name):
        site = Site.objects.get(name=site_name)
        self.fill_site_nodes(site)
        return site

    def increase_slivers(self, site_name, count):
        site = self.get_site(site_name)
        hpc_slice = self.get_hpc_slices()[0]
        while (len(site.availNodes) > 0) and (count > 0):
            node = site.availNodes.pop()
            hostname = node.name
            sliver = Sliver(name=node.name,
                            slice=hpc_slice,
                            node=node,
                            image = Image.objects.all()[0],
                            creator = User.objects.get(email="scott@onlab.us"),
                            deploymentNetwork=node.deployment,
                            numberCores = 1,
                            ip=socket.gethostbyname(hostname))
            sliver.save()

            print "created sliver", sliver

            site.hpcNodes.append(node)

            count = count - 1

    def decrease_slivers(self, site_name, count):
        site = self.get_site(site_name)
        hpc_slices = self.get_hpc_slices()
        while (len(site.hpcNodes) > 0) and (count > 0):
            node = site.hpcNodes.pop()
            for sliver in node.slivers.all():
                if sliver.slice in hpc_slices:
                     print "deleting sliver", sliver
                     sliver.delete()

            site.availNodes.append(node)
            count = count - 1

    def dump(self):
        print "slices:"
        for slice in self.get_hpc_slices():
            print "  ", slice

        print "sites:"
        print "%20s %10s %10s %10s %10s" % ("name", "avail", "hpc", "lat", "long")
        for site in self.get_sites():
            print "%20s %10d %10d %10s %10s" % (site.name, len(site.availNodes), len(site.hpcNodes), format_float(site.location.latitude), format_float(site.location.longitude))

        #print "slivers:"
        #for sliver in self.get_hpc_slivers():
        #    print "  ", sliver

if __name__=="__main__":
    x = HpcWizard()
    x.dump()

    x.increase_slivers("Princeton", 1)
    x.decrease_slivers("Princeton", 1)
