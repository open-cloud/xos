import os
from django.db import models
from django.core import exceptions
from plstackapi.core.models import PlCoreBase
from plstackapi.core.models import Flavor
from plstackapi.core.models import Image
from plstackapi.core.models import Key
from plstackapi.core.models import Slice
from plstackapi.core.models import Node
from plstackapi.core.models import Site
from plstackapi.core.models import DeploymentNetwork

# Create your models here.
class Sliver(PlCoreBase):
    instance_id = models.CharField(max_length=200, help_text="Nova instance id")    
    name = models.CharField(max_length=200, help_text="Sliver name")
    ip = models.GenericIPAddressField(help_text="Sliver ip address", blank=True, null=True)
    flavor = models.ForeignKey(Flavor, related_name='slivers')
    image = models.ForeignKey(Image, related_name='slivers')
    key = models.ForeignKey(Key, related_name='slivers')
    slice = models.ForeignKey(Slice, related_name='slivers')
    node = models.ForeignKey(Node, related_name='slivers')
    deploymentNetwork = models.ForeignKey(DeploymentNetwork, verbose_name='deployment', related_name='sliver_deploymentNetwork')

    def __unicode__(self):  return u'%s::%s' % (self.slice, self.deploymentNetwork)

    def save(self, *args, **kwds):
        if not self.slice.subnet.exists():
            raise exceptions.ValidationError, "Slice %s has no subnet" % self.slice.name

        if not self.instance_id:
            instance = self.driver.spawn_instance(name=self.name,
                                   key_name = self.key.name,
                                   flavor_id = self.flavor.flavor_id,
                                   image_id = self.image.image_id,
                                   hostname = self.node.name )
            self.instance_id = instance.id

        super(Sliver, self).save(*args, **kwds)

    def delete(self, *args, **kwds):
        if self.instance_id:
            self.driver.destroy_instance(self.instance_id)

        super(Sliver, self).delete(*args, **kwds)
