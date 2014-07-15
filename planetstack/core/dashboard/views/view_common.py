import os
import sys
from django.views.generic import TemplateView, View
import datetime
from pprint import pprint
import json
from syndicate.models import *
from core.models import *
from hpc.models import ContentProvider
from operator import attrgetter
from django import template
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseServerError, HttpResponseForbidden
from django.core import urlresolvers
from django.contrib.gis.geoip import GeoIP
from django.db.models import Q
from ipware.ip import get_ip
from operator import itemgetter, attrgetter
import traceback
import math

if os.path.exists("/home/smbaker/projects/vicci/cdn/bigquery"):
    sys.path.append("/home/smbaker/projects/vicci/cdn/bigquery")
else:
    sys.path.append("/opt/planetstack/hpc_wizard")
from planetstack_analytics import DoPlanetStackAnalytics, PlanetStackAnalytics, RED_LOAD, BLUE_LOAD

def getDashboardContext(user, context={}, tableFormat = False):
        context = {}

        userSliceData = getSliceInfo(user)
        if (tableFormat):
            context['userSliceInfo'] = userSliceTableFormatter(userSliceData)
        else:
            context['userSliceInfo'] = userSliceData
        context['cdnData'] = getCDNOperatorData(wait=False)
        context['cdnContentProviders'] = getCDNContentProviderData()

        (dashboards, unusedDashboards)= getDashboards(user)
        unusedDashboards=[x for x in unusedDashboards if x!="Customize"]
        context['dashboards'] = dashboards
        context['unusedDashboards'] = unusedDashboards

        return context

def getDashboards(user):
    dashboards = user.get_dashboards()

    dashboard_names = [d.name for d in dashboards]

    unused_dashboard_names = []
    for dashboardView in DashboardView.objects.all():
        if not dashboardView.name in dashboard_names:
            unused_dashboard_names.append(dashboardView.name)

    return (dashboard_names, unused_dashboard_names)

def getSliceInfo(user):
    sliceList = Slice.objects.all()
    slicePrivs = SlicePrivilege.objects.filter(user=user)
    userSliceInfo = []
    for entry in slicePrivs:

        slicename = Slice.objects.get(id=entry.slice.id).name
        slice = Slice.objects.get(name=Slice.objects.get(id=entry.slice.id).name)
        sliverList=Sliver.objects.all()
        sites_used = {}
        for sliver in slice.slivers.all():
             #sites_used['deploymentSites'] = sliver.node.deployment.name
             # sites_used[sliver.image.name] = sliver.image.name
             sites_used[sliver.node.site.name] = sliver.numberCores
        sliceid = Slice.objects.get(id=entry.slice.id).id
        try:
            sliverList = Sliver.objects.filter(slice=entry.slice.id)
            siteList = {}
            for x in sliverList:
               if x.node.site not in siteList:
                  siteList[x.node.site] = 1
            slivercount = len(sliverList)
            sitecount = len(siteList)
        except:
            traceback.print_exc()
            slivercount = 0
            sitecount = 0

        userSliceInfo.append({'slicename': slicename, 'sliceid':sliceid,
                              'sitesUsed':sites_used,
                              'role': SliceRole.objects.get(id=entry.role.id).role,
                              'slivercount': slivercount,
                              'sitecount':sitecount})

    return userSliceInfo

def getCDNContentProviderData():
    cps = []
    for dm_cp in ContentProvider.objects.all():
        cp = {"name": dm_cp.name,
              "account": dm_cp.account}
        cps.append(cp)

    return cps

def getCDNOperatorData(randomizeData = False, wait=True):
    HPC_SLICE_NAME = "HyperCache"

    bq = PlanetStackAnalytics()

    rows = bq.get_cached_query_results(bq.compose_cached_query(), wait)

    # wait=False on the first time the Dashboard is opened. This means we might
    # not have any rows yet. The dashboard code polls every 30 seconds, so it
    # will eventually pick them up.

    if rows:
        rows = bq.postprocess_results(rows, filter={"event": "hpc_heartbeat"}, maxi=["cpu"], count=["hostname"], computed=["bytes_sent/elapsed"], groupBy=["Time","site"], maxDeltaTime=80)

        # dictionaryize the statistics rows by site name
        stats_rows = {}
        for row in rows:
            stats_rows[row["site"]] = row
    else:
        stats_rows = {}

    slice = Slice.objects.filter(name=HPC_SLICE_NAME)
    if slice:
        slice_slivers = list(slice[0].slivers.all())
    else:
        slice_slivers = []

    new_rows = {}
    for site in Site.objects.all():
        # compute number of slivers allocated in the data model
        allocated_slivers = 0
        for sliver in slice_slivers:
            if sliver.node.site == site:
                allocated_slivers = allocated_slivers + 1

        stats_row = stats_rows.get(site.name,{})

        max_cpu = stats_row.get("max_avg_cpu", stats_row.get("max_cpu",0))
        cpu=float(max_cpu)/100.0
        hotness = max(0.0, ((cpu*RED_LOAD) - BLUE_LOAD)/(RED_LOAD-BLUE_LOAD))

        try:
           lat=float(site.location.latitude)
           long=float(site.location.longitude)
        except:
           lat=0
           long=0

        # format it to what that CDN Operations View is expecting
        new_row = {"lat": lat,
               "long": long,
               "health": 0,
               "numNodes": int(site.nodes.count()),
               "activeHPCSlivers": int(stats_row.get("count_hostname", 0)),     # measured number of slivers, from bigquery statistics
               "numHPCSlivers": allocated_slivers,                              # allocated number of slivers, from data model
               "siteUrl": str(site.site_url),
               "bandwidth": stats_row.get("sum_computed_bytes_sent_div_elapsed",0),
               "load": max_cpu,
               "hot": float(hotness)}
        new_rows[str(site.name)] = new_row

    # get rid of sites with 0 slivers that overlap other sites with >0 slivers
    for (k,v) in new_rows.items():
        bad=False
        if v["numHPCSlivers"]==0:
            for v2 in new_rows.values():
                if (v!=v2) and (v2["numHPCSlivers"]>=0):
                    d = haversine(v["lat"],v["long"],v2["lat"],v2["long"])
                    if d<100:
                         bad=True
            if bad:
                del new_rows[k]

    return new_rows

def slice_increase_slivers(user, user_ip, siteList, slice, count, noAct=False):
    sitesChanged = {}

    # let's compute how many slivers are in use in each node of each site
    for site in siteList:
        site.nodeList = list(site.nodes.all())
        for node in site.nodeList:
            node.sliverCount = 0
            for sliver in node.slivers.all():
                 if sliver.slice.id == slice.id:
                     node.sliverCount = node.sliverCount + 1

    # Allocate slivers to nodes
    # for now, assume we want to allocate all slivers from the same site
    nodes = siteList[0].nodeList
    while (count>0):
        # Sort the node list by number of slivers per node, then pick the
        # node with the least number of slivers.
        nodes = sorted(nodes, key=attrgetter("sliverCount"))
        node = nodes[0]

        print "adding sliver at node", node.name, "of site", node.site.name

        if not noAct:
            sliver = Sliver(name=node.name,
                        slice=slice,
                        node=node,
                        image = Image.objects.all()[0],
                        creator = User.objects.get(email=user),
                        deploymentNetwork=node.deployment,
                        numberCores =1 )
            sliver.save()

        node.sliverCount = node.sliverCount + 1

        count = count - 1

        sitesChanged[node.site.name] = sitesChanged.get(node.site.name,0) + 1

    return sitesChanged

def slice_decrease_slivers(user, siteList, slice, count, noAct=False):
    sitesChanged = {}
    if siteList:
        siteNames = [site.name for site in siteList]
    else:
        siteNames = None

    for sliver in list(slice.slivers.all()):
        if count>0:
            if(not siteNames) or (sliver.node.site.name in siteNames):
                sliver.delete()
                print "deleting sliver",sliver.name,"at node",sliver.node.name
                count=count-1
                sitesChanged[sliver.node.site.name] = sitesChanged.get(sliver.node.site.name,0) - 1

    return sitesChanged

def haversine(site_lat, site_lon, lat, lon):
    d=0
    if lat and lon and site_lat and site_lon:
        site_lat = float(site_lat)
        site_lon = float(site_lon)
        lat = float(lat)
        lon = float(lon)
        R = 6378.1
        a = math.sin( math.radians((lat - site_lat)/2.0) )**2 + math.cos( math.radians(lat) )*math.cos( math.radians(site_lat) )*(math.sin( math.radians((lon - site_lon)/2.0 ) )**2)
        c = 2 * math.atan2( math.sqrt(a), math.sqrt(1 - a) )
        d = R * c

    return d

def userSliceTableFormatter(data):
    formattedData = {
                     'rows' : data
                    }
    return formattedData
