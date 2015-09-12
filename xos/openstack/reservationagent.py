import datetime
import os
import sys
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")
import time
import django.utils
from core.models.instance import Instance
from core.models.reservation import Reservation, ReservedResource

class ReservationAgent:

    def run(self):
        while True :
            instances = {}

            tNow = django.utils.timezone.now()
            print "Processing reservations, tNow is %s" % tNow
            reservations = Reservation.objects.filter(startTime__lte = tNow)
            for reservation in reservations:
                print "  Processing reservation %s" % reservation
                if reservation.endTime <= tNow:
                    print "    deleting expired reservation"
                    reservation.delete()
                for reservedResource in reservation.reservedresources.all():
                    instance_resources = instances.get(reservedResource.instance.id, {})
                    instance_resources[reservedResource.resource.name] = reservedResource.quantity
                    instances[reservedResource.instance.id] = instance_resources

            print "Instance reservation set"
            for (instanceid, instance_resources) in instances.items():
                print "  instance", instanceid,
                for (name, value) in instance_resources.items():
                    print str(name)+":", value,
                print

            print "Updating instances"
            for instance in Instance.objects.all():
                instance_resv = instances.get(instance.id, {})
                numberCores = instance_resv.get("numberCores", 0)
                if numberCores != instance.numberCores:
                    print "instance %s setting numberCores to %s" % (instance.name, numberCores)
                    instance.numberCores = numberCores
                    instance.save()

            print "sleep"
            time.sleep(7)


if __name__ == '__main__':
    ReservationAgent().run()
                 
