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
        if not self.role_id:
            keystone_role = self.driver.create_role(name=self.role_type)
            self.role_id = keystone_role.id
        super(Role, self).save(*args, **kwds)
    
    def delete(self, *args, **kwds):
        if self.role_id:
            self.driver.delete_role({'id': self.role_id})   
        super(Role, self).delete(*args, **kwds)
            
