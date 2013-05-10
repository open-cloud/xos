import os
from django.db import models
from core.models import PlCoreBase

# Create your models here.

class Image(PlCoreBase):
    image_id = models.CharField(max_length=256, unique=True)
    name = models.CharField(max_length=256, unique=True)
    disk_format = models.CharField(max_length=256)
    container_format = models.CharField(max_length=256)

    def __unicode__(self):  return u'%s' % (self.name)
