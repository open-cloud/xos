import os
from django.db import models
from core.models import PlCoreBase
from core.models.plcorebase import StrippedCharField
from core.models import Deployment, DeploymentPrivilege, Controller,ControllerLinkManager,ControllerLinkDeletionManager

# Create your models here.

class Image(PlCoreBase):
    name = StrippedCharField(max_length=256, unique=True)
    disk_format = StrippedCharField(max_length=256)
    container_format = StrippedCharField(max_length=256)
    path = StrippedCharField(max_length=256, null=True, blank=True, help_text="Path to image on local disk")
    deployments = models.ManyToManyField('Deployment', through='ImageDeployments', blank=True, help_text="Select which images should be instantiated on this deployment", related_name='images')

    def __unicode__(self):  return u'%s' % (self.name)

class ImageDeployments(PlCoreBase):
    image = models.ForeignKey(Image,related_name='imagedeployments')
    deployment = models.ForeignKey(Deployment,related_name='imagedeployments')

    composite_primary_key = ('image', 'deployment')

    def __unicode__(self):  return u'%s %s' % (self.image, self.deployment)

    def can_update(self, user):
        return user.can_update_deployment(self.deployment)

class ControllerImages(PlCoreBase):
    objects = ControllerLinkManager()
    deleted_objects = ControllerLinkDeletionManager()
    image = models.ForeignKey(Image,related_name='controllerimages')
    controller = models.ForeignKey(Controller,related_name='controllerimages')
    glance_image_id = StrippedCharField(null=True, blank=True, max_length=200, help_text="Glance image id") 
    
    composite_primary_key = ('image', 'controller')
         
    def __unicode__(self):  return u'%s %s' % (self.image, self.controller)
