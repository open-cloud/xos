import os
from django.db import models
from core.models import PlCoreBase
from openstack.manager import OpenStackManager


# Create your models here.

class Key(PlCoreBase):
    name = models.CharField(max_length=256)
    nkey_id = models.CharField(null=True, blank=True, max_length=256, unique=True)
    key = models.CharField(max_length=512)
    type = models.CharField(max_length=256)
    blacklisted = models.BooleanField(default=False)

    def __unicode__(self):  return u'%s' % (self.key)

    def save(self, *args, **kwds):
        if not hasattr(self, 'os_manager'):
            setattr(self, 'os_manager', OpenStackManager())
            self.os_manager.save_key(self)
        super(Key, self).save(*args, **kwds)

    def delete(self, *args, **kwds):
        if not hasattr(self, 'os_manager'):
            setattr(self, 'os_manager', OpenStackManager())
            self.os_manager.delete_key(self)
        super(Key, self).delete(*args, **kwds) 
    
