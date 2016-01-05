import os
import sys
from django.views.generic import TemplateView, View
import datetime
from pprint import pprint
import json
from services.syndicate_storage.models import *
from core.models import *
from services.hpc.models import ContentProvider
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
from xos.config import Config, XOS_DIR

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
        instanceList=Instance.objects.all()
        sites_used = {}
        for instance in slice.instances.all():
             #sites_used['deploymentSites'] = instance.node.deployment.name
             # sites_used[instance.image.name] = instance.image.name
             sites_used[instance.node.site_deployment.site] = 1 #instance.numberCores
        sliceid = Slice.objects.get(id=entry.slice.id).id
        try:
            instanceList = Instance.objects.filter(slice=entry.slice.id)
            siteList = {}
            for x in instanceList:
               if x.node.site_deployment.site not in siteList:
                  siteList[x.node.site_deployment.site] = 1
            instancecount = len(instanceList)
            sitecount = len(siteList)
        except:
            traceback.print_exc()
            instancecount = 0
            sitecount = 0

        userSliceInfo.append({'slicename': slicename, 'sliceid':sliceid,
                              'sitesUsed':sites_used,
                              'role': SliceRole.objects.get(id=entry.role.id).role,
                              'instancecount': instancecount,
                              'sitecount':sitecount})

    return userSliceInfo

def slice_increase_instances(user, user_ip, siteList, slice, image, count, noAct=False):
    sitesChanged = {}

    # let's compute how many instances are in use in each node of each site
    for site in siteList:
        site.nodeList = list(site.nodes.all())
        for node in site.nodeList:
            node.instanceCount = 0
            for instance in node.instances.all():
                 if instance.slice.id == slice.id:
                     node.instanceCount = node.instanceCount + 1

    # Allocate instances to nodes
    # for now, assume we want to allocate all instances from the same site
    nodes = siteList[0].nodeList
    while (count>0):
        # Sort the node list by number of instances per node, then pick the
        # node with the least number of instances.
        nodes = sorted(nodes, key=attrgetter("instanceCount"))
        node = nodes[0]

        print "adding instance at node", node.name, "of site", node.site.name

        if not noAct:
            instance = Instance(name=node.name,
                        slice=slice,
                        node=node,
                        image = image,
                        creator = User.objects.get(email=user),
                        deploymentNetwork=node.deployment)
            instance.save()

        node.instanceCount = node.instanceCount + 1

        count = count - 1

        sitesChanged[node.site.name] = sitesChanged.get(node.site.name,0) + 1

    return sitesChanged

def slice_decrease_instances(user, siteList, slice, count, noAct=False):
    sitesChanged = {}
    if siteList:
        siteNames = [site.name for site in siteList]
    else:
        siteNames = None

    for instance in list(slice.instances.all()):
        if count>0:
            if(not siteNames) or (instance.node.site.name in siteNames):
                instance.delete()
                print "deleting instance",instance.name,"at node",instance.node.name
                count=count-1
                sitesChanged[instance.node.site.name] = sitesChanged.get(instance.node.site.name,0) - 1

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
