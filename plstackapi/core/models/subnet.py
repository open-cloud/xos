import os
from django.db import models
from plstackapi.core.models import PlCoreBase
from plstackapi.core.models import Slice
from plstackapi.openstack.driver import OpenStackDriver

# Create your models here.

class Subnet(PlCoreBase):
    subnet_id = models.CharField(max_length=256, unique=True)
    cidr = models.CharField(max_length=20)
    ip_version = models.IntegerField()
    start = models.IPAddressField()
    end = models.IPAddressField()
    slice = models.ForeignKey(Slice, related_name='subnet')

    def __unicode__(self):  return u'%s' % (self.name)

