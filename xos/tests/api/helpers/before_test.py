import dredd_hooks as hooks
import sys

# HELPERS
# NOTE move in separated module
import os
import sys
sys.path.append("/opt/xos")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")
import django
from core.models import *
from services.volt.models import *
from services.vsg.models import *
from services.vtr.models import *
import urllib2
import json
from django.utils import timezone
django.setup()


def doLogin(username, password):
    url = "http://127.0.0.1:8000/xoslib/login?username=%s&password=%s" % (username, password)
    res = urllib2.urlopen(url).read()
    parsed = json.loads(res)
    return {'token': parsed['xoscsrftoken'], 'sessionid': parsed['xossessionid']}


def cleanDB():
    # deleting all subscribers
    for s in CordSubscriberRoot.objects.all():
        s.delete(purge=True)

    # deleting all slices
    for s in Slice.objects.all():
        s.delete(purge=True)

    # deleting all Services
    for s in Service.objects.all():
        s.delete(purge=True)

    # deleting all Tenants
    for s in Tenant.objects.all():
        s.delete(purge=True)

    # deleting all Networks
    for s in Network.objects.all():
        s.delete(purge=True)

    # deleting all NetworkTemplates
    for s in NetworkTemplate.objects.all():
        s.delete(purge=True)

    for s in NetworkSlice.objects.all():
        s.delete(purge=True)

    for s in AddressPool.objects.all():
        s.delete(purge=True)

    for s in Flavor.objects.all():
        s.delete(purge=True)

    for s in Image.objects.all():
        s.delete(purge=True)

    # print 'DB Cleaned'


def createTestSubscriber():

    cleanDB()
    createFlavors()

    # load user
    user = User.objects.get(email="padmin@vicci.org")

    # network template
    private_template = NetworkTemplate()
    private_template.name = 'Private Network'
    private_template.save()

    # creating the test subscriber
    subscriber = CordSubscriberRoot(name='Test Subscriber 1', id=1)
    subscriber.created = timezone.now()
    subscriber.save()

    # vRouter service
    vrouter_service = VRouterService()
    vrouter_service.name = 'service_vrouter'
    vrouter_service.save()

    # address pools
    ap_vsg = AddressPool()
    ap_vsg.service = vrouter_service
    ap_vsg.name = 'addresses_vsg'
    ap_vsg.addresses = '10.168.0.0'
    ap_vsg.gateway_ip = '10.168.0.1'
    ap_vsg.gateway_mac = '02:42:0a:a8:00:01'
    ap_vsg.save()

    # print 'vRouter created'

    # Site
    site = Site.objects.get(name='mysite')

    # vSG service
    vsg_service = VSGService()
    vsg_service.name = 'service_vsg'

    # vSG slice
    vsg_slice = Slice(id=2)
    vsg_slice.name = site.login_base + "_testVsg"
    vsg_slice.service = vsg_service.id
    vsg_slice.site = site
    vsg_slice.caller = user

    vsg_slice.save()

    vsg_service.save()

    # volt service
    volt_service = VOLTService()
    volt_service.name = 'service_volt'
    volt_service.save()

    # cvpe image
    createImage('ubuntu-vcpe4')

    # vcpe slice
    vcpe_slice = Slice(id=3)
    vcpe_slice.name = site.login_base + "_testVcpe"
    vcpe_slice.service = Service.objects.get(kind='vCPE')
    vcpe_slice.site = site
    vcpe_slice.caller = user
    vcpe_slice.save()

    # print 'vcpe_slice created'

    # create a lan network
    lan_net = Network(id=1)
    lan_net.name = 'lan_network'
    lan_net.owner = vcpe_slice
    lan_net.template = private_template
    lan_net.save()

    # print 'lan_network created'

    # add relation between vcpe slice and lan network
    vcpe_network = NetworkSlice()
    vcpe_network.network = lan_net
    vcpe_network.slice = vcpe_slice
    vcpe_network.save()

    # print 'vcpe network relation added'

    # vbng service
    vbng_service = VBNGService()
    vbng_service.name = 'service_vbng'
    vbng_service.save()

    # print 'vbng_service creater'

    # volt tenant
    vt = VOLTTenant(subscriber=subscriber.id, id=1)
    vt.s_tag = "222"
    vt.c_tag = "432"
    vt.provider_service_id = volt_service.id
    vt.caller = user
    vt.save()

    # print "Subscriber Created"


def deleteTruckrolls():
    for s in VTRTenant.objects.all():
        s.delete(purge=True)


def setUpTruckroll():
    service_vtr = VTRService()
    service_vtr.name = 'service_vtr'
    service_vtr.save()


def createTruckroll():
    setUpTruckroll()
    tn = VTRTenant(id=1)
    tn.created = timezone.now()
    tn.save()


def createFlavors():
    small = Flavor(id=1)
    small.name = "m1.small"
    small.created = timezone.now()
    small.save()

    medium = Flavor(id=2)
    medium.name = "m1.medium"
    medium.created = timezone.now()
    medium.save()

    large = Flavor(id=3)
    large.name = "m1.large"
    large.created = timezone.now()
    large.save()


def createSlice():
    site = Site.objects.get(name='mysite')
    user = User.objects.get(email="padmin@vicci.org")

    sl = Slice(id=1)
    sl.created = timezone.now()
    sl.name = site.login_base + "_testSlice"
    sl.site = site
    sl.caller = user
    sl.save()
    return sl


def createDeployment():
    deployment = Deployment(id=1)
    deployment.created = timezone.now()
    deployment.name = 'MyTestDeployment'
    deployment.save()
    return deployment


def createImage(name):
    img = Image(id=1)
    img.name = name
    img.created = timezone.now()
    img.disk_format = 'QCOW2'
    img.kind = 'vm'
    img.save()
    return img


def createNode(deployment):
    site = Site.objects.get(name='mysite')

    site_deployment = SiteDeployment(id=1)
    site_deployment.site = site
    site_deployment.created = timezone.now()
    site_deployment.deployment = deployment
    site_deployment.save()

    node = Node(id=1)
    node.name = 'test-node'
    node.created = timezone.now()
    node.site = site
    node.site_deployment = site_deployment
    node.save()
    return node


def setupInstance():
    deployment = createDeployment()
    sl = createSlice()
    node = createNode(deployment)
    img = createImage('test-image')
    # print {'image': img.id, 'deployment': deployment.id, 'slice': sl.id}
    return {'image': img, 'deployment': deployment, 'slice': sl}


def createInstance():
    requirements = setupInstance()
    user = User.objects.get(email="padmin@vicci.org")

    instance = Instance(id=1)
    instance.name = 'test-instance'
    instance.created = timezone.now()
    instance.node = Node.objects.all()[0]
    instance.image = requirements['image']
    instance.slice = requirements['slice']
    instance.deployment = requirements['deployment']
    instance.caller = user
    instance.save()


def createService():
    service = Service(id=1)
    service.name = 'test-service'
    service.save()

# setupInstance()
# depl = createDeployment()
# createTestSubscriber()
# createInstance()
# createSlice()
# createNode(depl)
# createImage('test-image')
# createFlavors()
# createTruckroll()
# setUpTruckroll()
createService()
