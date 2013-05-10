import os
from django.db import models
from django.core import exceptions
from core.models import PlCoreBase
from core.models import Image
from core.models import Key
from core.models import Slice
from core.models import Node
from core.models import Site
from core.models import DeploymentNetwork
from openstack.manager import OpenStackManager

# Create your models here.
class Sliver(PlCoreBase):
    instance_id = models.CharField(null=True, blank=True, max_length=200, help_text="Nova instance id")    
    name = models.CharField(max_length=200, help_text="Sliver name")
    instance_name = models.CharField(blank=True, null=True, max_length=200, help_text="OpenStack generated name")
    ip = models.GenericIPAddressField(help_text="Sliver ip address", blank=True, null=True)
    image = models.ForeignKey(Image, related_name='slivers')
    key = models.ForeignKey(Key, related_name='slivers')
    slice = models.ForeignKey(Slice, related_name='slivers')
    node = models.ForeignKey(Node, related_name='slivers')
    deploymentNetwork = models.ForeignKey(DeploymentNetwork, verbose_name='deployment', related_name='sliver_deploymentNetwork')
    numberCores = models.IntegerField(verbose_name="Number of Cores", help_text="Number of cores for sliver", default=0)


    def __unicode__(self):  return u'%s' % (self.instance_name)

    def save(self, *args, **kwds):
        if not self.name:
            self.name = self.slice.name
        if not hasattr(self, 'os_manager'):
            setattr(self, 'os_manager', OpenStackManager())
            self.os_manager.save_sliver(self)
        super(Sliver, self).save(*args, **kwds)

    def delete(self, *args, **kwds):
        if not hasattr(self, 'os_manager'):
            setattr(self, 'os_manager', OpenStackManager())
            self.os_manager.delete_sliver(self)
        super(Sliver, self).delete(*args, **kwds)
