# NOT used, see https://github.com/apiaryio/dredd-hooks-python/issues/17#issuecomment-206950166

import os
import sys
sys.path.append("/opt/xos")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")
import django
from core.models import *
#from hpc.models import *
from services.cord.models import *
django.setup()


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


def createTestSubscriber():

    cleanDB()

    # load user
    user = User.objects.get(email="padmin@vicci.org")

    # network template
    private_template = NetworkTemplate()
    private_template.name = 'Private Network'
    private_template.save()

    # creating the test subscriber
    subscriber = CordSubscriberRoot(name='Test Subscriber 1', id=1)
    subscriber.save()

    # Site
    site = Site.objects.get(name='MySite')

    # vSG service
    vsg_service = VSGService()
    vsg_service.name = 'service_vsg'

    # vSG slice
    vsg_slice = Slice()
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

    # vcpe slice
    vcpe_slice = Slice()
    vcpe_slice.name = site.login_base + "_testVcpe"
    vcpe_slice.service = Service.objects.get(kind='vCPE')
    vcpe_slice.site = site
    vcpe_slice.caller = user
    vcpe_slice.save()

    print 'vcpe_slice created'

    # create a lan network
    lan_net = Network()
    lan_net.name = 'lan_network'
    lan_net.owner = vcpe_slice
    lan_net.template = private_template
    lan_net.save()

    print 'lan_network created'

    # add relation between vcpe slice and lan network
    vcpe_network = NetworkSlice()
    vcpe_network.network = lan_net
    vcpe_network.slice = vcpe_slice
    vcpe_network.save()

    print 'vcpe network relation added'

    # vbng service
    vbng_service = VBNGService()
    vbng_service.name = 'service_vbng'
    vbng_service.save()

    # volt tenant
    vt = VOLTTenant(subscriber=subscriber.id, id=1)
    vt.s_tag = "222"
    vt.c_tag = "432"
    vt.provider_service_id = volt_service.id
    vt.caller = user
    vt.save()

    print "Subscriber Created"

createTestSubscriber()
