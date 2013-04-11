import os
from django.db import models
from plstackapi.core.models import PlCoreBase
from plstackapi.core.models import User

# Create your models here.

class Key(PlCoreBase):
    name = models.CharField(max_length=256, unique=True)
    key = models.CharField(max_length=512)
    type = models.CharField(max_length=256)
    blacklisted = models.BooleanField(default=False)
    user = models.ForeignKey(User, related_name='keys')

    def __unicode__(self):  return u'%s' % (self.name)
