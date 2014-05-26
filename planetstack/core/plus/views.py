#views.py
import functools
import math
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
from ipware.ip import get_ip
from operator import itemgetter, attrgetter
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
        context = getDashboardContext(request.user, context)
        return self.render_to_response(context=context)

class DashboardDynamicView(TemplateView):
    head_template = r"""{% extends "admin/dashboard/dashboard_base.html" %}
       {% load admin_static %}
       {% block content %}
    """

    tail_template = r"{% endblock %}"

    def get(self, request, name="root", *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context = getDashboardContext(request.user, context)

        if name=="root":
            return self.multiDashboardView(request, context)
        else:
            return self.singleDashboardView(request, name, context)

    def readDashboard(self, fn):
        try:
            template= open("/opt/planetstack/templates/admin/dashboard/%s.html" % fn, "r").read()
            if (fn=="tenant"):
                # fix for tenant view - it writes html to a div called tabs-5
                template = '<div id="tabs-5"></div>' + template
            if (fn=="slice_interactions"):
                # fix for slice_interactions - it gives its container div a 40px
                # margin, and then positions it's header at -40px
                template = '<div id="tabs-4">' + template + '</div>'
            return template
        except:
            return "failed to open %s" % fn

    def multiDashboardView(self, request, context):
        head_template = self.head_template
        tail_template = self.tail_template

        body = """
         <div id="hometabs" >
         <ul id="suit_form_tabs" class="nav nav-tabs nav-tabs-suit" data-tab-prefix="suit-tab">
        """

        dashboards = request.user.get_dashboards()

        # customize is a special dashboard they always get
        customize = DashboardView.objects.filter(name="Customize")
        if customize:
            dashboards.append(customize[0])

        for i,view in enumerate(dashboards):
            body = body + '<li><a href="#dashtab-%d">%s</a></li>\n' % (i, view.name)

        body = body + "</ul>\n"

        for i,view in enumerate(dashboards):
            url = view.url
            body = body + '<div id="dashtab-%d">\n' % i
            if url.startswith("template:"):
                fn = url[9:]
                body = body + self.readDashboard(fn)
            body = body + '</div>\n'

        body=body+"</div>\n"

        t = template.Template(head_template + body + self.tail_template)

        response_kwargs = {}
        response_kwargs.setdefault('content_type', self.content_type)
        return self.response_class(
            request = request,
            template = t,
            context = context,
            **response_kwargs)

    def singleDashboardView(self, request, name, context):
        head_template = self.head_template
        tail_template = self.tail_template

        t = template.Template(head_template + self.readDashboard(fn) + self.tail_template)

        response_kwargs = {}
        response_kwargs.setdefault('content_type', self.content_type)
        return self.response_class(
            request = request,
            template = t,
            context = context,
            **response_kwargs)

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
    #dashboards = sorted(list(user.dashboardViews.all()), key=attrgetter('order'))
    dashboards = user.get_dashboards()

    dashboard_names = [d.name for d in dashboards]

    unused_dashboard_names = []
    for dashboardView in DashboardView.objects.all():
        if not dashboardView.name in dashboard_names:
            unused_dashboard_names.append(dashboardView.name)

    return (dashboard_names, unused_dashboard_names)

class TenantCreateSlice(View):
    def post(self, request, *args, **kwargs):
        if request.user.isReadOnlyUser():
            return HttpResponseForbidden("User is in read-only mode")

        sliceName = request.POST.get("sliceName", "0")
        serviceClass = request.POST.get("serviceClass", "0")
        imageName = request.POST.get("imageName", "0")
        actionToDo = request.POST.get("actionToDo", "0")
        networkPorts = request.POST.get("network","0")
        mountDataSets = request.POST.get("mountDataSets","0")
        privateVolume = request.POST.get("privateVolume","0")
        if (actionToDo == "add"):
           serviceClass = ServiceClass.objects.get(name=serviceClass)
           site = request.user.site
           image = Image.objects.get(name=imageName)
           newSlice = Slice(name=sliceName,serviceClass=serviceClass,site=site,imagePreference=image,mountDataSets=mountDataSets)
           newSlice.save()
	   privateTemplate="Private"
	   publicTemplate="Public shared IPv4"
	   privateNetworkName = sliceName+"-"+privateTemplate
	   publicNetworkName = sliceName+"-"+publicTemplate
	   slice=Slice.objects.get(name=sliceName)
	   addNetwork(privateNetworkName,privateTemplate,slice)
	   addNetwork(publicNetworkName,publicTemplate,slice)
	   addOrModifyPorts(networkPorts,sliceName)
	   if privateVolume=="true":
	   	privateVolForSlice(request.user,sliceName)
        return HttpResponse("Slice created")

def privateVolForSlice(user,sliceName):
	if not hasPrivateVolume(sliceName):
	   volumeName=createPrivateVolume(user,sliceName)
	   readWrite="true"
	   mountVolume(sliceName,volumeName,readWrite)

class TenantUpdateSlice(View):
    def post(self, request, *args, **kwargs):
        if request.user.isReadOnlyUser():
            return HttpResponseForbidden("User is in read-only mode")

        sliceName = request.POST.get("sliceName", "0")
        serviceClass = request.POST.get("serviceClass", "0")
        imageName = request.POST.get("imageName", "0")
        actionToDo = request.POST.get("actionToDo", "0")
        networkPorts = request.POST.get("networkPorts","0")
        dataSet = request.POST.get("dataSet","0")
        privateVolume = request.POST.get("privateVolume","0")
        slice = Slice.objects.all()
        for entry in slice:
                serviceClass = ServiceClass.objects.get(name=serviceClass)
                if(entry.name==sliceName):
                         if (actionToDo == "update"):
                                setattr(entry,'serviceClass',serviceClass)
                                setattr(entry,'imagePreference',imageName)
                                setattr(entry,'mountDataSets',dataSet)
                                entry.save()
                                break
	addOrModifyPorts(networkPorts,sliceName)
	if privateVolume=="true":
                privateVolForSlice(request.user,sliceName)
        return HttpResponse("Slice updated")

def addNetwork(name,template,sliceName):
	networkTemplate=NetworkTemplate.objects.get(name=template)
	newNetwork = Network(name = name,
                              template = networkTemplate,
                              owner = sliceName)
        newNetwork.save()
	addNetworkSlice(newNetwork,sliceName)

def addNetworkSlice(networkSlice,sliceName):
	newNetworkSlice=NetworkSlice(network =networkSlice,
				     slice=sliceName)
	newNetworkSlice.save()

def addOrModifyPorts(networkPorts,sliceName):
	networkList = Network.objects.all()
        networkInfo = []
        if networkPorts:
           for networkEntry in networkList:
               networkSlices = networkEntry.slices.all()
               for slice in networkSlices:
                   if slice.name==sliceName:
                          if networkEntry.template.name=="Public shared IPv4":
                             setattr(networkEntry,'ports',networkPorts)
                             networkEntry.save()

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
    tenantSliceDetails['deploymentSites']=userSliceTableFormatter(getDeploymentSites())
    tenantSliceDetails['sites'] = userSliceTableFormatter(getTenantSitesInfo())
    tenantSliceDetails['mountDataSets'] = userSliceTableFormatter(getMountDataSets())
    tenantSliceDetails['publicKey'] = getPublicKey(user)
    return tenantSliceDetails

def getTenantInfo(user):
    slices =Slice.objects.all()
    userSliceInfo = []
    for entry in slices:
       sliceName = Slice.objects.get(id=entry.id).name
       slice = Slice.objects.get(name=Slice.objects.get(id=entry.id).name)
       sliceServiceClass = entry.serviceClass.name
       preferredImage =  entry.imagePreference
       #sliceDataSet = entry.mountDataSets
       sliceNetwork = {}
       numSliver = 0
       sliceImage=""
       sliceSite = {}
       sliceNode = {}
       sliceInstance= {}
       #createPrivateVolume(user,sliceName)
       for sliver in slice.slivers.all():
	    if sliver.node.site.name in BLESSED_SITES:
                sliceSite[sliver.node.site.name] = sliceSite.get(sliver.node.site.name,0) + 1
                sliceImage = sliver.image.name
                sliceNode[str(sliver)] = sliver.node.name
       numSliver = sum(sliceSite.values())
       numSites = len(sliceSite)
       userSliceInfo.append({'sliceName': sliceName,'sliceServiceClass': sliceServiceClass,'preferredImage':preferredImage,'numOfSites':numSites, 'sliceSite':sliceSite,'sliceImage':sliceImage,'numOfSlivers':numSliver,'instanceNodePair':sliceNode})
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

def getPublicKey(user):
	users=User.objects.all()
        for key in users:
        	if (str(key.email)==str(user)):
                    	sshKey = key.public_key
        return sshKey

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

def createPrivateVolume(user, sliceName):
    caps = Volume.CAP_READ_DATA | Volume.CAP_WRITE_DATA | Volume.CAP_HOST_DATA
    getattr(Volume.default_gateway_caps,"read data") | \
           getattr(Volume.default_gateway_caps,"write data") | \
           getattr(Volume.default_gateway_caps,"host files")
    v = Volume(name="private_" + sliceName, owner_id=user, description="private volume for %s" % sliceName, blocksize=61440, private=True, archive=False, default_gateway_caps = caps)
    v.save()
    return v

SYNDICATE_REPLICATE_PORTNUM = 1025

def get_free_port():
    inuse={}
    inuse[SYNDICATE_REPLICATE_PORTNUM] = True
    for vs in VolumeSlice.objects.all():
        inuse[vs.peer_portnum]=True
        inuse[vs.replicate_portnum]=True
    for network in Network.objects.all():
        if not network_ports:
            continue
        network_ports = [x.strip() for x in network.ports.split(",")]
        for network_port in network_ports:
            try:
                inuse[int(network_port)] = True
            except:
                # in case someone has put a malformed port number in the list
                pass
    for i in range(1025, 65535):
        if not inuse.get(i,False):
            return i
    return False

def mountVolume(sliceName, volumeName, readWrite):
    slice = Slice.objects.get(name=sliceName)
    volume = Volume.objects.get(name=volumeName)
    # choose some unused port numbers
    flags = Volume.CAP_READ_DATA
    if readWrite:
        flags = flags | Volume.CAP_WRITE_DATA
    vs = VolumeSlice(volume_id = volume, slice_id = slice, gateway_caps=flags, peer_portnum = get_free_port(), replicate_portnum = SYNDICATE_REPLICATE_PORTNUM)
    vs.save()

def hasPrivateVolume(sliceName):
     slice = Slice.objects.get(name=sliceName)
     for vs in VolumeSlice.objects.filter(slice_id=slice):
         if vs.volume_id.private:
             return True
     return False

def getMountDataSets():
        dataSetInfo=[]
        for volume in Volume.objects.all():
            if not volume.private:
                dataSetInfo.append({'DataSet': volume.name})

        return dataSetInfo

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

def getPageSummary(request):
    slice = request.GET.get('slice', None)
    site = request.GET.get('site', None)
    node = request.GET.get('node', None)

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
        return HttpResponse(json.dumps(getDashboardContext(request.user, tableFormat=True)), mimetype='application/javascript')

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
                if request.user.isReadOnlyUser():
                    return HttpResponseForbidden("User is in read-only mode")
                sliceName = request.POST.get("sliceName",None)
                slice = Slice.objects.get(name=sliceName)
                #print slice, slice.id
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
            if len(x)==0:
                return 0
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

        if request.user.isReadOnlyUser():
            return HttpResponseForbidden("User is in read-only mode")

        if (actionToDo == "add"):
            user_ip = request.GET.get("ip", get_ip(request))
            slice_increase_slivers(request.user, user_ip, siteList, slice, 1)
        elif (actionToDo == "rem"):
            slice_decrease_slivers(request.user, siteList, slice, 1)

        print '*' * 50
        print 'Ask for site: ' + siteName + ' to ' + actionToDo + ' another HPC Sliver'
        return HttpResponse(json.dumps("Success"), mimetype='application/javascript')

class DashboardAjaxView(View):
    def get(self, request, **kwargs):
        return HttpResponse(json.dumps(getCDNOperatorData(True)), mimetype='application/javascript')

class DashboardAnalyticsAjaxView(View):
    def get(self, request, name="hello_world", **kwargs):
        if (name == "hpcSummary"):
            return HttpResponse(json.dumps(hpc_wizard.get_hpc_wizard().get_summary_for_view()), mimetype='application/javascript')
        elif (name == "hpcUserSite"):
            return HttpResponse(json.dumps(getDashboardContext(request.user, tableFormat=True)), mimetype='application/javascript')
        elif (name == "hpcMap"):
            return HttpResponse(json.dumps(getCDNOperatorData(True)), mimetype='application/javascript')
        elif (name == "bigquery"):
            (mimetype, data) = DoPlanetStackAnalytics(request)
            return HttpResponse(data, mimetype=mimetype)
        else:
            return HttpResponse(json.dumps("Unknown"), mimetype='application/javascript')

class DashboardCustomize(View):
    def post(self, request, *args, **kwargs):
        if request.user.isReadOnlyUser():
            return HttpResponseForbidden("User is in read-only mode")

        dashboards = request.POST.get("dashboards", None)
        if not dashboards:
            dashboards=[]
        else:
            dashboards = [x.strip() for x in dashboards.split(",")]
            dashboards = [DashboardView.objects.get(name=x) for x in dashboards]

        request.user.dashboardViews.all().delete()

        for i,dashboard in enumerate(dashboards):
            udbv = UserDashboardView(user=request.user, dashboardView=dashboard, order=i)
            udbv.save()

        return HttpResponse(json.dumps("Success"), mimetype='application/javascript')

