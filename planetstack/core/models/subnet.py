import os
import commands    
from django.db import models
from core.models import PlCoreBase
from core.models import Slice
from openstack.manager import OpenStackManager

# Create your models here.

class Subnet(PlCoreBase):
    subnet_id = models.CharField(max_length=256, unique=True)
    cidr = models.CharField(max_length=20)
    ip_version = models.IntegerField()
    start = models.IPAddressField()
    end = models.IPAddressField()
    slice = models.ForeignKey(Slice, related_name='subnet')

    def __unicode__(self):  return u'%s' % (self.slice.name)

    def save(self, *args, **kwds):
        if not hasattr(self, 'os_manager'):
            setattr(self, 'os_manager', OpenStackManager())
            self.os_manager.save_subnet(self)
        super(Subnet, self).save(*args, **kwds)

    def delete(self, *args, **kwds):
        if not hasattr(self, 'os_manager'):
            setattr(self, 'os_manager', OpenStackManager())
            self.os_manager.delete_subnet(self)
        super(Subnet, self).delete(*args, **kwds)
