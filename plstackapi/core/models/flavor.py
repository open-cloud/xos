import os
from django.db import models
from plstackapi.core.models import PlCoreBase

# Create your models here.

class Flavor(PlCoreBase):
    flavor_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=256, unique=True)
    memory_mb = models.IntegerField()
    disk_gb = models.IntegerField()
    vcpus = models.IntegerField()

    def __unicode__(self):  return u'%s' % (self.name)
