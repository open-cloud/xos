import datetime
import os
import operator
import socket
import pytz
import json
import random
import sys
import time

if os.path.exists("/home/smbaker/projects/vicci/plstackapi/planetstack"):
    sys.path.append("/home/smbaker/projects/vicci/plstackapi/planetstack")
else:
    sys.path.append("/opt/planetstack")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "planetstack.settings")
from django import db
from django.db import connection
from core.models import Slice, Sliver, ServiceClass, Reservation, Tag, Network, User, Node, Image, Deployment, Site, NetworkTemplate, NetworkSlice, Service
from hpc.models import HpcService, ServiceProvider, ContentProvider, OriginServer, CDNPrefix, HpcService

# amount of time in milliseconds which will be queried for HPC statistics.
QUERY_TIME=150000

# Constants used for computing 'hotness'
#    BLUE_LOAD = MB/s which should be a "0" on the hotness scale
#    RED_LOAD = MB/s which should be a "1" on the hotness scale
BLUE_LOAD=5000000
RED_LOAD=15000000

MAX_LOAD=RED_LOAD

def log(what, showdate=True):
    try:
        if showdate:
            file("/tmp/scott-hpcwizard.log", "a").write(time.strftime("%Y-%m-%d %H:%M:%S ", time.gmtime()))
        file("/tmp/scott-hpcwizard.log", "a").write("%s\n" % what)
    except:
        pass # uh oh

def log_exc(what):
    log(what)
    log(traceback.format_exc(), showdate=False)

def avg(x):
    return float(sum(x))/len(x)

def format_float(x):
    try:
        return "%10.5f" % x
    except:
        return str(x)

class HpcWizard:
    def __init__(self):
        try:
            self.hpcService = HpcService.objects.get()
        except:
            # OpenCloud.us currently has a Service object instantiated instead
            # of a HpcService. Fallback for now.
            self.hpcService = Service.objects.get(name="HPC Service")

        self.hpcQueryThread = None

    def get_hpc_slices(self):
        try:
            slices = self.hpcService.slices.all()
        except:
            # BUG in data model -- Slice.service has related name 'service' and
            #                      it should be 'slices'
            slices = self.hpcService.service.all()
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

    def merge_site_statistics(self, sites):
        """ this does it based on the sumb of all bandwidth

            The issue here is that we the computed load reacts immediately to
            the addition or deletion of nodes. i.e. 5 nodes at 80% + 1 node at
            0% = average load 66%.
        """
        site_dict = {}
        for site in self.hpcQueryThread.site_rows:
            site_dict[site["site"]] = site

        for site in sites:
            if site.name in site_dict:
                site.bytes_sent = site_dict[site.name]["sum_bytes_sent"]
                time_delta = site_dict[site.name]["time_delta"]
                computed_duration = (int(time_delta/30)+1)*30
                if (computed_duration > 0):
                    site.bandwidth = site.bytes_sent/computed_duration
                if len(site.hpcNodes)>0:
                    # figure out how many bytes_sent would be represented
                    # by blue and red
                    blue_load = len(site.hpcNodes) * BLUE_LOAD * computed_duration
                    red_load = len(site.hpcNodes) * RED_LOAD * computed_duration
                    max_load = len(site.hpcNodes) * MAX_LOAD * computed_duration

                    site.hotness = (min(red_load, max(blue_load, float(site.bytes_sent))) - blue_load)/(red_load-blue_load)
                    site.load = int(min(100, site.bytes_sent*100/max_load))

                    file("/tmp/scott2.txt","a").write("%s %d %0.2f %0.2f %0.2f %0.2f %d\n" % (site.name, site.bytes_sent, blue_load, red_load, site.hotness, time_delta, computed_duration))

    def merge_site_statistics_new(self, sites):
        """ This does it based on max load

            Advantage of this method is that since we're effectively reporting
            the maximally loaded node, we don't get instantaneous reactions
            to adding additional nodes. On the contrary, it will take a while
            for the load to balance from the loaded node to the new less-loaded
            node.
        """
        site_dict = {}
        for site in self.hpcQueryThread.site_rows:
            site_dict[site["site"]] = site

        for site in sites:
            if site.name in site_dict:
                site.max_avg_bandwidth = site_dict[site.name]["max_avg_bandwidth"]
                site.bytes_sent = site_dict[site.name]["sum_bytes_sent"]

                site.hotness = min(1.0, float(max(BLUE_LOAD, site.max_avg_bandwidth) - BLUE_LOAD) / (RED_LOAD-BLUE_LOAD))
                site.load = int(site.max_avg_bandwidth*100/MAX_LOAD)

                # we still need site["bandwidth"] for the summary statistics
                time_delta = site_dict[site.name]["time_delta"]
                computed_duration = (int(time_delta/30)+1)*30
                if (computed_duration > 0):
                    site.bandwidth = site.bytes_sent/computed_duration
                else:
                    site.bandwidth = 0

                if len(site.hpcNodes)>0:
                    file("/tmp/scott3.txt","a").write("%s %d %0.2f %d %0.2f\n" % (site.name, site.bytes_sent, site.hotness, site.load, site.bandwidth))

    def get_sites(self):
        sites = list(Site.objects.all())

        for site in sites:
            self.fill_site_nodes(site, self.get_hpc_slivers())
            site.load = 0
            site.hotness = 0
            site.bandwidth = 0
            site.numNodes = len(site.hpcNodes) + len(site.availNodes)

        if (self.hpcQueryThread is not None) and (self.hpcQueryThread.is_stalled()):
            self.initialize_statistics()

        # merge in the statistics data if it is available
        if self.hpcQueryThread and self.hpcQueryThread.data_version>0:
            self.merge_site_statistics(sites)

        # django will leak extraordinary amounts of memory without this line
        db.reset_queries()

        return sites

    def get_nodes_to_sites(self):
        nodes_to_sites = {}

        sites = list(Site.objects.all())

        for site in sites:
            for node in site.nodes.all():
                nodes_to_sites[node.name] = site.name

        return nodes_to_sites

    def get_slice_sites(self, slice_name):
        sites = list(Site.objects.all())
        slivers = list(Slice.objects.get(name=slice_name).slivers.all())
        for site in sites:
            self.fill_site_nodes(site, slivers)
        return sites

    def get_sites_for_view(self):
        sites = {}
        for site in self.get_sites():
            if site.name in ["ON.Lab", "I2 Atlanta"]:
                continue

            d = {"lat": float(site.location.latitude),
                 "long": float(site.location.longitude),
                 "health": 0,
                 "numNodes": site.numNodes,
                 "numHPCSlivers": len(site.hpcNodes),
                 "siteUrl": str(site.site_url),
                 "hot": getattr(site,"hotness",0.0),
                 "load": getattr(site,"load",0)}
            sites[str(site.name)] = d

        import pprint
        f = file("/tmp/scott.txt","w")
        pprint.pprint(sites, f)
        f.close()

        return sites

    def get_summary_for_view(self):
        total_slivers = 0
        total_bandwidth = 0
        average_cpu = 0

        sites = [site for site in self.get_sites() if len(site.hpcNodes)>0]

        total_slivers = sum( [len(site.hpcNodes) for site in sites] )
        total_bandwidth = sum( [site.bandwidth for site in sites] )
        average_cpu = int(avg( [site.load for site in sites] ))

        return {"total_slivers": total_slivers,
                "total_bandwidth": total_bandwidth,
                "average_cpu": average_cpu}

    def initialize_statistics(self):
        from query import HpcQueryThread

        if (self.hpcQueryThread is not None):
            log("dropping old query thread")
            self.hpcQueryThread.please_die = True
            self.hpcQueryThread = None

        log("launching new query thread")

        nodes_to_sites = self.get_nodes_to_sites()
        self.hpcQueryThread = HpcQueryThread(nodes_to_sites = nodes_to_sites, timeStart=-QUERY_TIME, slice="HyperCache")

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
        print "%20s %10s %10s %10s %10s %10s %10s" % ("name", "avail", "hpc", "lat", "long", "sent", "hot")
        for site in self.get_sites():
            print "%20s %10d %10d %10s %10s %10d %10.2f" % (site.name,
                                                            len(site.availNodes),
                                                            len(site.hpcNodes),
                                                            format_float(site.location.latitude),
                                                            format_float(site.location.longitude),
                                                            getattr(site,"bytes_sent",0),
                                                            getattr(site,"hotness",0.5))

        #print "slivers:"
        #for sliver in self.get_hpc_slivers():
        #    print "  ", sliver

glo_hpc_wizard = None

def get_hpc_wizard():
    global glo_hpc_wizard

    if (glo_hpc_wizard is None):
        glo_hpc_wizard = HpcWizard()
        glo_hpc_wizard.initialize_statistics()

    return glo_hpc_wizard

def main():
    x = HpcWizard()

    # initialized the Statistics thread, and wait for some data to show up
    x.initialize_statistics()
    while x.hpcQueryThread.data_version==0:
       time.sleep(1)

    x.dump()

    # quick test of the increase / decrease functions

    x.increase_slivers("Princeton", 1)
    x.decrease_slivers("Princeton", 1)

if __name__=="__main__":
    main()

