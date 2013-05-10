import os
from django.db import models
from core.models import PlCoreBase

# Create your models here.

class Key(PlCoreBase):
    name = models.CharField(max_length=256, unique=True)
    nkey_id = models.CharField(max_length=256, unique=True)
    key = models.CharField(max_length=512)
    type = models.CharField(max_length=256)
    blacklisted = models.BooleanField(default=False)

    def __unicode__(self):  return u'%s' % (self.name)

    def save(self, *args, **kwds):
        self.os_manager.save_key(self)
        super(Key, self).save(*args, **kwds)

    def delete(self, *args, **kwds):
        self.os_manager.delete_key(self)
        super(Key, self).delete(*args, **kwds) 
    
