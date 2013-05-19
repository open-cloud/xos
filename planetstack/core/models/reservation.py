import os
import datetime
from django.db import models
from core.models import PlCoreBase
from core.models import Sliver
from core.models import Slice
from core.models import ServiceResource

# Create your models here.

class Reservation(PlCoreBase):
    startTime = models.DateTimeField()
    slice = models.ForeignKey(Slice, related_name="reservations")
    duration = models.IntegerField(default=1)

    def __unicode__(self):  return u'%s duration %d' % (self.startTime, self.duration)

    @property
    def endTime(self):
        return self.startTime + datetime.timedelta(hours=self.duration)

class ReservedResource(PlCoreBase):
    sliver = models.ForeignKey(Sliver, related_name="reservedResourrces")
    resource = models.ForeignKey(ServiceResource, related_name="reservedResources")
    quantity = models.IntegerField(default=1)
    reservationSet = models.ForeignKey(Reservation, related_name="reservedResources")

    class Meta(PlCoreBase.Meta):
       verbose_name_plural = "Reserved Resources"

    def __unicode__(self):  return u'%d %s on %s' % (self.quantity, self.resource, self.sliver)




