import os
import datetime
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from core.models import PlCoreBase
from core.models.plcorebase import StrippedCharField

class Role(PlCoreBase):

    role_type = StrippedCharField(max_length=80, verbose_name="Name")
    role = StrippedCharField(max_length=80, verbose_name="Keystone role id", null=True, blank=True)
    description = StrippedCharField(max_length=120, verbose_name="Description")
    content_type = models.ForeignKey(ContentType, verbose_name="Role Scope")

    def __unicode__(self):  return u'%s:%s' % (self.content_type,self.role_type)


    def save(self, *args, **kwds):
        super(Role, self).save(*args, **kwds)
    
    def delete(self, *args, **kwds):
        super(Role, self).delete(*args, **kwds)
            
