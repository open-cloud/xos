import os
from django.db import models
from plstackapi.core.models import PlCoreBase
from plstackapi.core.models import Flavor
from plstackapi.core.models import Image
from plstackapi.core.models import Key
from plstackapi.core.models import Slice
from plstackapi.core.models import Node
from plstackapi.core.models import Site
from plstackapi.core.models import DeploymentNetwork
from plstackapi.openstack.driver import OpenStackDriver

# Create your models here.
class Sliver(PlCoreBase):
    instance_id = models.CharField(max_length=200, help_text="Nova instance id")    
    name = models.CharField(max_length=200, help_text="Sliver name")
    flavor = models.ForeignKey(Flavor, related_name='slivers')
    image = models.ForeignKey(Image, related_name='slivers')
    key = models.ForeignKey(Key, related_name='slivers')
    slice = models.ForeignKey(Slice, related_name='slivers')
    node = models.ForeignKey(Node, related_name='slivers')
    site = models.ForeignKey(Site, related_name='slivers')
    deploymentNetwork = models.ForeignKey(DeploymentNetwork, related_name='sliver_deploymentNetwork')

    def __unicode__(self):  return u'%s::%s' % (self.slice, self.deploymentNetwork)

