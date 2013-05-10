import os
import datetime
from django.db import models
from core.models import PlCoreBase
from openstack.manager import OpenStackManager

class Role(PlCoreBase):

    #ROLE_CHOICES = (('admin', 'Admin'), ('pi', 'Principle Investigator'), ('user','User'))
    role = models.CharField(null=True, blank=True,max_length=256, unique=True)
    role_type = models.CharField(max_length=80, unique=True)

    def __unicode__(self):  return u'%s' % (self.role_type)


    def save(self, *args, **kwds):
        if not hasattr(self, 'os_manager'):
            setattr(self, 'os_manager', OpenStackManager())
            self.os_manager.save_role(self)
        super(Role, self).save(*args, **kwds)
    
    def delete(self, *args, **kwds):
        if not hasattr(self, 'os_manager'):
            setattr(self, 'os_manager', OpenStackManager())
            self.os_manager.delete_role(self)   
        super(Role, self).delete(*args, **kwds)
            
