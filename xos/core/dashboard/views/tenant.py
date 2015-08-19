from view_common import *
from core.models import *
import functools
from django.contrib.auth.models import BaseUserManager
from django.core import serializers
from django.core.mail import EmailMultiAlternatives
import json

BLESSED_DEPLOYMENTS = ["US-MaxPlanck", "US-GeorgiaTech", "US-Princeton", "US-Washington", "US-Stanford"]

class RequestAccessView(View):
    def post(self, request, *args, **kwargs):
	email = request.POST.get("email", "0")
	firstname = request.POST.get("firstname", "0")
	lastname = request.POST.get("lastname", "0")
	site = request.POST.get("site","0")
        # see if it already exists
        user=User.objects.filter(email=BaseUserManager.normalize_email(email))
        if (user):
             user = user[0]
             if user.is_active:
                 # force a new email to be sent
                 user.is_registering=True
                 user.save()
                 return HttpResponse(json.dumps({"error": "already_approved"}), content_type='application/javascript')
             else:
                 return HttpResponse(json.dumps({"error": "already_pending"}), content_type='application/javascript')

        user=User.deleted_objects.filter(email=BaseUserManager.normalize_email(email))
        if (user):
            return HttpResponse(json.dumps({"error": "is_deleted"}), content_type='application/javascript')

	user = User(
            email=BaseUserManager.normalize_email(email),
            firstname=firstname,
            lastname=lastname,
	    is_active=False,
            is_admin=False,
            is_registering=True
        )
        user.save()
	user.site=Site.objects.get(name=site)
	user.save(update_fields=['site'])
	sitePriv = SitePrivilege.objects.filter(site=user.site)
	userId = user.id
	userUrl = "http://"+request.get_host()+"/admin/core/user/"+str(userId)
	for sp in sitePriv:
		subject, from_email, to = 'Authorize OpenCloud User Account', 'support@opencloud.us', str(sp.user)
		text_content = 'This is an important message.'
		html_content = """<p>Please authorize the following user on site """+site+""": <br><br>User: """+firstname+""" """+lastname+"""<br>Email: """+email+"""<br><br>
Check the checkbox next to Is Active property at <a href="""+userUrl+"""> this link</a> to authorize the user, and then click the Save button. If you do not recognize this individual, or otherwise do not want to approve this account, please ignore this email. If you do not approve this request in 48 hours, the account will automatically be deleted.</p>"""
		msg = EmailMultiAlternatives(subject,text_content, from_email, [to])
		msg.attach_alternative(html_content, "text/html")
		msg.send()
        return HttpResponse(serializers.serialize("json",[user,]), content_type='application/javascript')

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
        userEmail = request.POST.get("userEmail","0")
        if (actionToDo == "add"):
           serviceClass = ServiceClass.objects.get(name=serviceClass)
           site = request.user.site
           image = Image.objects.get(name=imageName)
           newSlice = Slice(name=sliceName,serviceClass=serviceClass,site=site,image_preference=image,mount_data_sets=mountDataSets)
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
	   slicePrivs=SlicePrivilege(user=User.objects.get(email=userEmail),slice=Slice.objects.get(name=sliceName),role=SliceRole.objects.get(role="admin"))
           slicePrivs.save()
        return HttpResponse(json.dumps("Slice created"), content_type='application/javascript')

class TenantAddUser(View):
    def post(self, request, *args, **kwargs):
        if request.user.isReadOnlyUser():
            return HttpResponseForbidden("User is in read-only mode")

        sliceName = request.POST.get("sliceName", "0")
        userEmail = request.POST.get("userEmail","0")
        slicePrivs=SlicePrivilege(user=User.objects.get(email=userEmail),slice=Slice.objects.get(name=sliceName),role=SliceRole.objects.get(role="admin"))
        slicePrivs.save()
        return HttpResponse(json.dumps("Slice created"), content_type='application/javascript')

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
                                setattr(entry,'image_preference',imageName)
                                setattr(entry,'mount_data_sets',dataSet)
                                entry.save()
                                break
	addOrModifyPorts(networkPorts,sliceName)
	if privateVolume=="true":
                privateVolForSlice(request.user,sliceName)
        return HttpResponse(json.dumps("Slice updated"), content_type='application/javascript')

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
    #tenantSliceDetails['sites'] = userSliceTableFormatter(getTenantSitesInfo())
    tenantSliceDetails['mountDataSets'] = userSliceTableFormatter(getMountDataSets())
    tenantSliceDetails['publicKey'] = getPublicKey(user)
    tenantSliceDetails['availableSites']=userSliceTableFormatter(getAvailableSites())
    tenantSliceDetails['role']=getUserRole(user)
    tenantSliceDetails['siteUsers']=getSiteUsers(user)
    return tenantSliceDetails

def getSiteUsers(user):
	users = User.objects.filter(site=user.site)
	siteUsers=[]
        for entry in users:
		siteUsers.append(str(entry))
	return siteUsers


def getUserRole(user):
	sp=SitePrivilege.objects.filter(user=user)
	for entry in sp:
		return str(entry.role)


def getTenantInfo(user):
    slices =Slice.objects.all()
    userSliceInfo = []
    for entry in slices:
       if (entry.site == user.site):
           sliceName = Slice.objects.get(id=entry.id).name
           slice = Slice.objects.get(name=Slice.objects.get(id=entry.id).name)
           sliceServiceClass = entry.serviceClass.name
           preferredImage =  entry.image_preference
           #sliceDataSet = entry.mount_data_sets
           sliceNetwork = {}
           numInstance = 0
           sliceImage=""
           sliceSite = {}
           sliceNode = {}
           sliceInstance= {}
           #createPrivateVolume(user,sliceName)
           available_sites = getAvailableSites()
           for instance in slice.instances.all():
                if instance.node.site.name in available_sites:
                    sliceSite[instance.node.site.name] = sliceSite.get(instance.node.site.name,0) + 1
                    sliceImage = instance.image.name
                    sliceNode[str(instance)] = instance.node.name
           numInstance = sum(sliceSite.values())
           numSites = len(sliceSite)
           userSliceInfo.append({'sliceName': sliceName,'sliceServiceClass': sliceServiceClass,'preferredImage':preferredImage,'numOfSites':numSites, 'sliceSite':sliceSite,'sliceImage':sliceImage,'numOfInstances':numInstance,'instanceNodePair':sliceNode})
    return userSliceInfo

def getTenantSitesInfo():
        availableSites=getAvailableSites()
	tenantSiteInfo=[]
        for entry in Site.objects.all():
            if entry.name in availableSites:
		 tenantSiteInfo.append({'siteName':entry.name})
	return tenantSiteInfo

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
    #imageList = Image.objects.all()
    #imageInfo = []
    #for imageEntry in imageList:
          #imageInfo.append({'Image':imageEntry.name})
    imageInfo = []
    tempImageInfo = []
    length = len(BLESSED_DEPLOYMENTS)
    for deployment in Deployment.objects.all():
        if deployment.name in BLESSED_DEPLOYMENTS:
            for x in deployment.imagedeployments.all():
                tempImageInfo.append(x.image.name)
    temp = {}
    for i in set(tempImageInfo):
    	temp[i] = tempImageInfo.count(i)
    for key in temp:
	if temp[key]>1:
		imageInfo.append(key)
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
        if not network.ports:
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

def getAvailableSites():
    available_sites = []
    for deployment in Deployment.objects.all():
        if deployment.name in BLESSED_DEPLOYMENTS:
            for x in deployment.sitedeployments.all():
		if x.site.nodes.all():
                	available_sites.append(x.site.name)
    return list(set(available_sites))

class TenantDeleteSliceView(View):
        def post(self,request):
                if request.user.isReadOnlyUser():
                    return HttpResponseForbidden("User is in read-only mode")
                sliceName = request.POST.get("sliceName",None)
                slice = Slice.objects.get(name=sliceName)
                #print slice, slice.id
                sliceToDel=Slice(name=sliceName, id=slice.id)
                sliceToDel.delete()
                return HttpResponse(json.dumps("Slice deleted"), content_type='application/javascript')

class TenantAddOrRemoveInstanceView(View):
    """ Add or remove instances from a Slice

        Arguments:
            siteName - name of site. If not specified, XOS will pick the
                       best site.,
            actionToDo - [add | rem]
            count - number of instances to add or remove
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
	imageName = request.POST.get("image",None)
        noAct = request.POST.get("noAct", False)

        if not sliceName:
            return HttpResponseServerError("No slice name given")

        slice = Slice.objects.get(name=sliceName)
	image = Image.objects.get(name=imageName)

        if siteName:
            siteList = [Site.objects.get(name=siteName)]
        else:
            siteList = None

        if (actionToDo == "add"):
            user_ip = request.GET.get("ip", get_ip(request))
            if (siteList is None):
                siteList = tenant_pick_sites(user, user_ip, slice, count)

            sitesChanged = slice_increase_instances(request.user, user_ip, siteList, slice, image, count, noAct)
        elif (actionToDo == "rem"):
            sitesChanged = slice_decrease_instances(request.user, siteList, slice, count, noAct)
        else:
            return HttpResponseServerError("Unknown actionToDo %s" % actionToDo)

        return HttpResponse(json.dumps(sitesChanged), content_type='application/javascript')

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
        return HttpResponse(json.dumps(sites), content_type='application/javascript')

def siteSortKey(site, slice=None, count=None, lat=None, lon=None):
    # try to pick a site we're already using
    has_instances_here=False
    if slice:
        for instance in slice.instances.all():
            if instance.node.site.name == site.name:
                has_instances_here=True

    # Haversine method
    d = haversine(site.location.latitude, site.location.longitude, lat, lon)

    return (-has_instances_here, d)

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

    available_sites = getAvailableSites()
    sites = Site.objects.all()
    sites = [x for x in sites if x.name in available_sites]
    sites = sorted(sites, key=functools.partial(siteSortKey, slice=slice, count=count, lat=lat, lon=lon))

    return sites

class TenantViewData(View):
    def get(self, request, **kwargs):
        return HttpResponse(json.dumps(getTenantSliceInfo(request.user, True)), content_type='application/javascript')

class RequestAccountView(View):
    def get(self, request, **kwargs):
        return HttpResponse()
