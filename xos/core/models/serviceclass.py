import os
from django.db import models
from core.models import PlCoreBase

def get_default_serviceclass():
    try:
        return ServiceClass.objects.get(name="Best Effort")
    except ServiceClass.DoesNotExist:
        return None

class ServiceClass(PlCoreBase):
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=255)
    commitment = models.IntegerField(default=365)
    membershipFee = models.IntegerField(default=0)
    membershipFeeMonths = models.IntegerField(default=12)
    upgradeRequiresApproval = models.BooleanField(default=False)
    upgradeFrom = models.ManyToManyField('self', blank=True, null=True)

    class Meta(PlCoreBase.Meta):
       verbose_name_plural = "Service classes"

    def __unicode__(self):  return u'%s' % (self.name)

    def save_by_user(self, user, *args, **kwds):
        if self.can_update(user):
            super(ServiceClass, self).save(*args, **kwds)
