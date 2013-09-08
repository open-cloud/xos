import os
import datetime
from django.db import models
from core.models import PlCoreBase
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

class Role(PlCoreBase):

    role_type = models.CharField(max_length=80, verbose_name="Name")
    description = models.CharField(max_length=120, verbose_name="Description")
    content_type = models.ForeignKey(ContentType, verbose_name="Role Scope")

    def __unicode__(self):  return u'%s:%s' % (self.content_type,self.role_type)


    def save(self, *args, **kwds):
        if not hasattr(self, 'os_manager'):
            from openstack.manager import OpenStackManager
            setattr(self, 'os_manager', OpenStackManager())
        self.os_manager.save_role(self)
        super(Role, self).save(*args, **kwds)
    
    def delete(self, *args, **kwds):
        if not hasattr(self, 'os_manager'):
            from openstack.manager import OpenStackManager
            setattr(self, 'os_manager', OpenStackManager())
        self.os_manager.delete_role(self)   
        super(Role, self).delete(*args, **kwds)
            
