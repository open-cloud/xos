#views.py
import functools
import math
import os
import sys
from django.views.generic import TemplateView, View
import datetime
from pprint import pprint
import json
from core.models import *
from hpc.models import ContentProvider
from operator import attrgetter
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseServerError
from django.core import urlresolvers
from django.contrib.gis.geoip import GeoIP
from ipware.ip import get_ip
import traceback
import socket

BLESSED_SITES = ["Stanford", "Washington", "Princeton", "GeorgiaTech", "MaxPlanck"]

if os.path.exists("/home/smbaker/projects/vicci/cdn/bigquery"):
    sys.path.append("/home/smbaker/projects/vicci/cdn/bigquery")
else:
    sys.path.append("/opt/planetstack/hpc_wizard")
import hpc_wizard
from planetstack_analytics import DoPlanetStackAnalytics, PlanetStackAnalytics, RED_LOAD, BLUE_LOAD

class DashboardWelcomeView(TemplateView):
    template_name = 'admin/dashboard/welcome.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        userDetails = getUserSliceInfo(request.user)
        #context['site'] = userDetails['site']

        context['userSliceInfo'] = userDetails['userSliceInfo']
        context['cdnData'] = userDetails['cdnData']
        context['cdnContentProviders'] = userDetails['cdnContentProviders']
        return self.render_to_response(context=context)

def getUserSliceInfo(user, tableFormat = False):
        userDetails = {}

        userSliceData = getSliceInfo(user)
        if (tableFormat):
#            pprint("*******      GET USER SLICE INFO")
            userDetails['userSliceInfo'] = userSliceTableFormatter(userSliceData)
        else:
            userDetails['userSliceInfo'] = userSliceData
        userDetails['cdnData'] = getCDNOperatorData(wait=False)
        userDetails['cdnContentProviders'] = getCDNContentProviderData()
        return userDetails

class TenantCreateSlice(View):
    def post(self, request, *args, **kwargs):
        sliceName = request.POST.get("sliceName", "0")
        serviceClass = request.POST.get("serviceClass", "0")
        imageName = request.POST.get("imageName", "0")
        actionToDo = request.POST.get("actionToDo", "0")
        network = request.POST.get("network","0")
        mountDataSets = request.POST.get("mountDataSets","0")
        if (actionToDo == "add"):
           serviceClass = ServiceClass.objects.get(name=serviceClass)
           site = request.user.site
           image = Image.objects.get(name=imageName)
           newSlice = Slice(name=sliceName,serviceClass=serviceClass,site=site,imagePreference=image,mountDataSets=mountDataSets,network=network)
           newSlice.save()
        return HttpResponse("Slice created")

class TenantUpdateSlice(View):
    def post(self, request, *args, **kwargs):
        sliceName = request.POST.get("sliceName", "0")
        serviceClass = request.POST.get("serviceClass", "0")
        imageName = request.POST.get("imageName", "0")
        actionToDo = request.POST.get("actionToDo", "0")
        network = request.POST.get("network","0")
        dataSet = request.POST.get("dataSet","0")
        slice = Slice.objects.all()
        for entry in slice:
                serviceClass = ServiceClass.objects.get(name=serviceClass)
                if(entry.name==sliceName):
                         if (actionToDo == "update"):
                                setattr(entry,'serviceClass',serviceClass)
                                setattr(entry,'imagePreference',imageName)
                                setattr(entry,'network',network)
                                setattr(entry,'mountDataSets',dataSet)
                                entry.save()
                                break
        return HttpResponse("Slice updated")

def  update_slice(sliceName,**fields):
         slice = Slice.objects.filter(name = sliceName)
         for (k,v) in fields.items():
                setattr(slice, k, v)
                slice.save()
         return slice

def getTenantSliceInfo(user, tableFormat = False):
    tenantSliceDetails = {}
    tenantSliceData = getTenantInfo(user)
    tenantServiceClassData = getServiceClassInfo(user)
    if (tableFormat):
       tenantSliceDetails['userSliceInfo'] = userSliceTableFormatter(tenantSliceData)
       tenantSliceDetails['sliceServiceClass']=userSliceTableFormatter(tenantServiceClassData)
    else:
       tenantSliceDetails['userSliceInfo'] = tenantSliceData
    tenantSliceDetails['sliceServiceClass']=userSliceTableFormatter(tenantServiceClassData)
    tenantSliceDetails['image']=userSliceTableFormatter(getImageInfo(user))
    tenantSliceDetails['network']=userSliceTableFormatter(getNetworkInfo(user))
    tenantSliceDetails['deploymentSites']=userSliceTableFormatter(getDeploymentSites())
    tenantSliceDetails['sites'] = userSliceTableFormatter(getTenantSitesInfo())
    tenantSliceDetails['mountDataSets'] = userSliceTableFormatter(getMountDataSets())
    return tenantSliceDetails


def getTenantInfo(user):
    slices =Slice.objects.all()
    userSliceInfo = []
    for entry in slices:
       sliceName = Slice.objects.get(id=entry.id).name
       slice = Slice.objects.get(name=Slice.objects.get(id=entry.id).name)
       sliceServiceClass = entry.serviceClass.name
       preferredImage =  entry.imagePreference
       sliceDataSet = entry.mountDataSets
       sliceNetwork = entry.network
       numSliver = 0
       sliceImage=""
       sliceSite = {}
       sliceNode = {}
       sliceInstance= {}
       for sliver in slice.slivers.all():
	    if sliver.node.site.name in BLESSED_SITES:
                sliceSite[sliver.node.site.name] = sliceSite.get(sliver.node.site.name,0) + 1
                sliceImage = sliver.image.name
                sliceNode[str(sliver)] = sliver.node.name
       numSliver = sum(sliceSite.values())
       numSites = len(sliceSite)
       userSliceInfo.append({'sliceName': sliceName,'sliceServiceClass': sliceServiceClass,'preferredImage':preferredImage,'numOfSites':numSites, 'sliceSite':sliceSite,'sliceImage':sliceImage,'numOfSlivers':numSliver,'sliceDataSet':sliceDataSet,'sliceNetwork':sliceNetwork, 'instanceNodePair':sliceNode})
    return userSliceInfo

def getTenantSitesInfo():
	tenantSiteInfo=[]
        for entry in Site.objects.all():
            if entry.name in BLESSED_SITES:
		 tenantSiteInfo.append({'siteName':entry.name})
	return tenantSiteInfo

def userSliceTableFormatter(data):
#    pprint(data)
    formattedData = {
                     'rows' : data
                    }
    return formattedData

def getServiceClassInfo(user):
    serviceClassList = ServiceClass.objects.all()
    sliceInfo = []
    for entry in serviceClassList:
          sliceInfo.append({'serviceClass':entry.name})
    return sliceInfo

def getImageInfo(user):
    imageList = Image.objects.all()
    #imageList = ['Fedora 16 LXC rev 1.3','Hadoop','MPI']
    imageInfo = []
    for imageEntry in imageList:
          imageInfo.append({'Image':imageEntry.name})
          #imageInfo.append({'Image':imageEntry})
    return imageInfo

def getMountDataSets():
        dataSetList = ['------','GenBank','LSST','LHC','NOAA','Measurement Lab','Common Crawl']
        dataSetInfo = []
        for entry in dataSetList:
                dataSetInfo.append({'DataSet':entry})
        return dataSetInfo

def getNetworkInfo(user):
   #networkList = Network.objects.all()
    networkList = ['Private Only','Private and Publicly Routable']
    networkInfo = []
    for networkEntry in networkList:
          #networkInfo.append({'Network':networkEntry.name})
          networkInfo.append({'Network':networkEntry})
    return networkInfo

def getDeploymentSites():
    deploymentList = Deployment.objects.all()
    deploymentInfo = []
    for entry in deploymentList:
        deploymentInfo.append({'DeploymentSite':entry.name})
    return deploymentInfo

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

    rows = bq.get_cached_query_results(bq.compose_latest_query(groupByFields=["%hostname", "event", "%slice"]), wait)

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

    slice = Slice.objects.get(name=HPC_SLICE_NAME)
    slice_slivers = list(slice.slivers.all())

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

        # format it to what that CDN Operations View is expecting
        new_row = {"lat": float(site.location.longitude),
               "long": float(site.location.longitude),
               "lat": float(site.location.latitude),
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

class SimulatorView(View):
    def get(self, request, **kwargs):
        sim = json.loads(file("/tmp/simulator.json","r").read())
        text = "<html><head></head><body>"
        text += "Iteration: %d<br>" % sim["iteration"]
        text += "Elapsed since report %d<br><br>" % sim["elapsed_since_report"]
        text += "<table border=1>"
        text += "<tr><th>site</th><th>trend</th><th>weight</th><th>bytes_sent</th><th>hot</th></tr>"
        for site in sim["site_load"].values():
            text += "<tr>"
            text += "<td>%s</td><td>%0.2f</td><td>%0.2f</td><td>%d</td><td>%0.2f</td>" % \
                        (site["name"], site["trend"], site["weight"], site["bytes_sent"], site["load_frac"])
            text += "</tr>"
        text += "</table>"
        text += "</body></html>"
        return HttpResponse(text)

class DashboardUserSiteView(View):
    def get(self, request, **kwargs):
        return HttpResponse(json.dumps(getUserSliceInfo(request.user, True)), mimetype='application/javascript')

class TenantViewData(View):
    def get(self, request, **kwargs):
        return HttpResponse(json.dumps(getTenantSliceInfo(request.user, True)), mimetype='application/javascript')

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

def siteSortKey(site, slice=None, count=None, lat=None, lon=None):
    # try to pick a site we're already using
    has_slivers_here=False
    if slice:
        for sliver in slice.slivers.all():
            if sliver.node.site.name == site.name:
                has_slivers_here=True

    # Haversine method
    d = haversine(site.location.latitude, site.location.longitude, lat, lon)

    return (-has_slivers_here, d)

def tenant_pick_sites(user, user_ip=None, slice=None, count=None):
    """ Returns list of sites, sorted from most favorable to least favorable """
    lat=None
    lon=None
    try:
        client_geo = GeoIP().city(user_ip)
        if client_geo:
            lat=float(client_geo["latitude"])
            lon=float(client_geo["longitude"])
    except:
        print "exception in geo code"
        traceback.print_exc()

    sites = Site.objects.all()
    sites = [x for x in sites if x.name in BLESSED_SITES]
    sites = sorted(sites, key=functools.partial(siteSortKey, slice=slice, count=count, lat=lat, lon=lon))

    return sites

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
    sliverList ={}
    if siteList:
        siteNames = [site.name for site in siteList]
    else:
        siteNames = None

    for sliver in slice.slivers.all():
        if(not siteNames) or (sliver.node.site.name in siteNames):
                node = sliver.node
                sliverList[sliver.name]=node.name

    for key in sliverList:
        if count>0:
            sliver = Sliver.objects.filter(name=key)[0]
            sliver.delete()
            print "deleting sliver",sliverList[key],"at node",sliver.node.name
            count=count-1
            sitesChanged[sliver.node.site.name] = sitesChanged.get(sliver.node.site.name,0) - 1

    return sitesChanged

class TenantDeleteSliceView(View):
        def post(self,request):
                sliceName = request.POST.get("sliceName",None)
                slice = Slice.objects.get(name=sliceName)
                print slice, slice.id
                sliceToDel=Slice(name=sliceName, id=slice.id)
                sliceToDel.delete()
                return HttpResponse("Slice deleted")

class TenantAddOrRemoveSliverView(View):
    """ Add or remove slivers from a Slice

        Arguments:
            siteName - name of site. If not specified, PlanetStack will pick the
                       best site.,
            actionToDo - [add | rem]
            count - number of slivers to add or remove
            sliceName - name of slice
            noAct - if set, no changes will be made to db, but result will still
                    show which sites would have been modified.

        Returns:
            Dictionary of sites that were modified, and the count of nodes
            that were added or removed at each site.
    """
    def post(self, request, *args, **kwargs):
        siteName = request.POST.get("siteName", None)
        actionToDo = request.POST.get("actionToDo", None)
        count = int(request.POST.get("count","0"))
	sliceName = request.POST.get("slice", None)
        noAct = request.POST.get("noAct", False)

        if not sliceName:
            return HttpResponseServerError("No slice name given")

        slice = Slice.objects.get(name=sliceName)

        if siteName:
            siteList = [Site.objects.get(name=siteName)]
        else:
            siteList = None

        if (actionToDo == "add"):
            user_ip = request.GET.get("ip", get_ip(request))
            if (siteList is None):
                siteList = tenant_pick_sites(user, user_ip, slice, count)

            sitesChanged = slice_increase_slivers(request.user, user_ip, siteList, slice, count, noAct)
        elif (actionToDo == "rem"):
            sitesChanged = slice_decrease_slivers(request.user, siteList, slice, count, noAct)
        else:
            return HttpResponseServerError("Unknown actionToDo %s" % actionToDo)

        return HttpResponse(json.dumps(sitesChanged), mimetype='application/javascript')

    def get(self, request, *args, **kwargs):
        request.POST = request.GET
        return self.post(request, *args, **kwargs)  # for testing REST in browser
        #return HttpResponseServerError("GET is not supported")

class TenantPickSitesView(View):
    """ primarily just for testing purposes """
    def get(self, request, *args, **kwargs):
        count = request.GET.get("count","0")
	slice = request.GET.get("slice",None)
        if slice:
            slice = Slice.objects.get(name=slice)
        ip = request.GET.get("ip", get_ip(request))
        sites = tenant_pick_sites(request.user, user_ip=ip, count=0, slice=slice)
        sites = [x.name for x in sites]
        return HttpResponse(json.dumps(sites), mimetype='application/javascript')

class DashboardSummaryAjaxView(View):
    def get(self, request, **kwargs):
        def avg(x):
            return float(sum(x))/len(x)

        sites = getCDNOperatorData().values()

        sites = [site for site in sites if site["numHPCSlivers"]>0]

        total_slivers = sum( [site["numHPCSlivers"] for site in sites] )
        total_bandwidth = sum( [site["bandwidth"] for site in sites] )
        average_cpu = int(avg( [site["load"] for site in sites] ))

        result= {"total_slivers": total_slivers,
                "total_bandwidth": total_bandwidth,
                "average_cpu": average_cpu}

        return HttpResponse(json.dumps(result), mimetype='application/javascript')

class DashboardAddOrRemoveSliverView(View):
    # TODO: deprecate this view in favor of using TenantAddOrRemoveSliverView

    def post(self, request, *args, **kwargs):
        siteName = request.POST.get("site", None)
        actionToDo = request.POST.get("actionToDo", "0")

        siteList = [Site.objects.get(name=siteName)]
        slice = Slice.objects.get(name="HyperCache")

        if (actionToDo == "add"):
            user_ip = request.GET.get("ip", get_ip(request))
            slice_increase_slivers(request.user, user_ip, siteList, slice, 1)
        elif (actionToDo == "rem"):
            slice_decrease_slivers(request.user, siteList, slice, 1)

        print '*' * 50
        print 'Ask for site: ' + siteName + ' to ' + actionToDo + ' another HPC Sliver'
        return HttpResponse('This is POST request ')

class DashboardAjaxView(View):
    def get(self, request, **kwargs):
        return HttpResponse(json.dumps(getCDNOperatorData(True)), mimetype='application/javascript')

class DashboardAnalyticsAjaxView(View):
    def get(self, request, name="hello_world", **kwargs):
        if (name == "hpcSummary"):
            return HttpResponse(json.dumps(hpc_wizard.get_hpc_wizard().get_summary_for_view()), mimetype='application/javascript')
        elif (name == "hpcUserSite"):
            return HttpResponse(json.dumps(getUserSliceInfo(request.user, True)), mimetype='application/javascript')
        elif (name == "hpcMap"):
            return HttpResponse(json.dumps(getCDNOperatorData(True)), mimetype='application/javascript')
        elif (name == "bigquery"):
            (mimetype, data) = DoPlanetStackAnalytics(request)
            return HttpResponse(data, mimetype=mimetype)
        else:
            return HttpResponse(json.dumps("Unknown"), mimetype='application/javascript')

