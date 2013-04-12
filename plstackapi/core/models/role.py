import os
import datetime
from django.db import models
from plstackapi.core.models import PlCoreBase

# Create your models here.

class Role(PlCoreBase):

    ROLE_CHOICES = (('admin', 'Admin'), ('pi', 'Principle Investigator'), ('user','User'))
    role_id = models.CharField(max_length=256, unique=True)
    role_type = models.CharField(max_length=80, unique=True, choices=ROLE_CHOICES)

    def __unicode__(self):  return u'%s' % (self.role_type)

