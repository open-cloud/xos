import os
import sys
sys.path.append("/opt/xos")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")
import django
from core.models import *
#from hpc.models import *
from services.cord.models import *
django.setup()

def createTestSubscriber():
    # deleting all subscribers
    for s in CordSubscriberRoot.objects.all():
        print(s.name)
        s.delete(purge=True)
    
    # creating the test subscriber
    subscriber = CordSubscriberRoot(name='Test Subscriber 1')
    subscriber.save()
    print "Subscriber Created"
