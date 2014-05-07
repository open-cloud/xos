import os
from django.db import models
from core.models import PlCoreBase
from core.models import Deployment

# Create your models here.

class Image(PlCoreBase):
    name = models.CharField(max_length=256, unique=True)
    disk_format = models.CharField(max_length=256)
    container_format = models.CharField(max_length=256)
    path = models.CharField(max_length=256, null=True, blank=True, help_text="Path to image on local disk")

    def __unicode__(self):  return u'%s' % (self.name)

class ImageDeployments(PlCoreBase):
    image = models.ForeignKey(Image)
    deployment = models.ForeignKey(Deployment)
    glance_image_id = models.CharField(null=True, blank=True, max_length=200, help_text="Glance image id") 

    def __unicode__(self):  return u'%s %s' % (self.image, self.deployment)

    
