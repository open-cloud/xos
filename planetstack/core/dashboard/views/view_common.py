import os
import sys
from django.views.generic import TemplateView, View
import datetime
from pprint import pprint
import json
from syndicate_storage.models import *
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

def getDashboardContext(user, context={}, tableFormat = False):
        context = {}

        userSliceData = getSliceInfo(user)
        if (tableFormat):
            context['userSliceInfo'] = userSliceTableFormatter(userSliceData)
        else:
            context['userSliceInfo'] = userSliceData
#        context['cdnData'] = getCDNOperatorData(wait=False)
#        context['cdnContentProviders'] = getCDNContentProviderData()

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
        # do not show disabled dashboard views
        if not dashboardView.enabled:
            continue
        if not dashboardView.name in dashboard_names:
            unused_dashboard_names.append(dashboardView.name)

    return (dashboard_names, unused_dashboard_names)

def getSliceInfo(user):
    sliceList = Slice.objects.all()
    slicePrivs = SlicePrivilege.objects.filter(user=user)
    userSliceInfo = []
    for entry in slicePrivs:

        slice = Slice.objects.filter(id=entry.slice.id)
        if not slice:
            # the privilege is to a slice that doesn't exist
            print "data model consistency problem, slice %s doesn't exist" % entry.slice.id
            continue
        slice = slice[0]
        slicename = slice.name
        sliverList=Sliver.objects.all()
        sites_used = {}
        for sliver in slice.slivers.all():
             #sites_used['deploymentSites'] = sliver.node.deployment.name
             # sites_used[sliver.image.name] = sliver.image.name
             sites_used[sliver.node.site_deployment.site] = 1 #sliver.numberCores
        sliceid = Slice.objects.get(id=entry.slice.id).id
        try:
            sliverList = Sliver.objects.filter(slice=entry.slice.id)
            siteList = {}
            for x in sliverList:
               if x.node.site_deployment.site not in siteList:
                  siteList[x.node.site_deployment.site] = 1
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

def slice_increase_slivers(user, user_ip, siteList, slice, image, count, noAct=False):
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
                        image = image,
                        creator = User.objects.get(email=user),
                        deploymentNetwork=node.deployment)
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
