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
    flavor = models.ForeignKey(Flavor, related_name='sliver_flavor')
    image = models.ForeignKey(Image, related_name='sliver_image')
    key = models.ForeignKey(Key, related_name='sliver_key')
    slice = models.ForeignKey(Slice, related_name='sliver_slice')
    node = models.ForeignKey(Node, related_name='sliver_node')
    site = models.ForeignKey(Site, related_name='sliver_site')
    deploymentNetwork = models.ForeignKey(DeploymentNetwork, related_name='sliver_deploymentNetwork')

    def __unicode__(self):  return u'%s::%s' % (self.slice, self.siteDeploymentNetwork)

    def save(self, *args, **kwds):
        driver  = OpenStackDriver()
        instance = driver.spawn_instances(name=self.name,
                                          keyname=self.name,
                                          hostnames=self.node.name,
                                          flavor=self.flavor.name,
                                          image=self.image.name)
        self.instance_id = instance.id
        super(Sliver, self).save(*args, **kwds)

    def delete(self, *args, **kwds):
        driver  = OpenStackDriver()
        driver.destroy_instance(name=self.name, id=self.instance_id)
        super(Sliver, self).delete(*args, **kwds)

