import os
import datetime
from django.db import models
from plstackapi.core.models import PlCoreBase

class Role(PlCoreBase):

    #ROLE_CHOICES = (('admin', 'Admin'), ('pi', 'Principle Investigator'), ('user','User'))
    role_id = models.CharField(max_length=256, unique=True)
    role_type = models.CharField(max_length=80, unique=True)

    def __unicode__(self):  return u'%s' % (self.role_type)


    def save(self, *args, **kwds):
        self.os_manager.save_role(self)
        super(Role, self).save(*args, **kwds)
    
    def delete(self, *args, **kwds):
        self.os_manager.delete_role(self)   
        super(Role, self).delete(*args, **kwds)
            
