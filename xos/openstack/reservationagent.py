import datetime
import os
import sys
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")
import time
import django.utils
from core.models.sliver import Sliver
from core.models.reservation import Reservation, ReservedResource

class ReservationAgent:

    def run(self):
        while True :
            slivers = {}

            tNow = django.utils.timezone.now()
            print "Processing reservations, tNow is %s" % tNow
            reservations = Reservation.objects.filter(startTime__lte = tNow)
            for reservation in reservations:
                print "  Processing reservation %s" % reservation
                if reservation.endTime <= tNow:
                    print "    deleting expired reservation"
                    reservation.delete()
                for reservedResource in reservation.reservedresources.all():
                    sliver_resources = slivers.get(reservedResource.sliver.id, {})
                    sliver_resources[reservedResource.resource.name] = reservedResource.quantity
                    slivers[reservedResource.sliver.id] = sliver_resources

            print "Sliver reservation set"
            for (sliverid, sliver_resources) in slivers.items():
                print "  sliver", sliverid,
                for (name, value) in sliver_resources.items():
                    print str(name)+":", value,
                print

            print "Updating slivers"
            for sliver in Sliver.objects.all():
                sliver_resv = slivers.get(sliver.id, {})
                numberCores = sliver_resv.get("numberCores", 0)
                if numberCores != sliver.numberCores:
                    print "sliver %s setting numberCores to %s" % (sliver.name, numberCores)
                    sliver.numberCores = numberCores
                    sliver.save()

            print "sleep"
            time.sleep(7)


if __name__ == '__main__':
    ReservationAgent().run()
                 
