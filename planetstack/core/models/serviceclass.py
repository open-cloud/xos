import os
from django.db import models
from core.models import PlCoreBase
from core.models import Site
from core.models import DeploymentNetwork

# Create your models here.

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

    @staticmethod
    def get_default():
        try:
            return ServiceClass.objects.get(name="Best Effort")
        except ServiceClass.DoesNotExist:
            return None


