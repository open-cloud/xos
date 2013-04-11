import os
from django.db import models
from plstackapi.core.models import PlCoreBase
from plstackapi.core.models import Site
from plstackapi.core.models import DeploymentNetwork

# Create your models here.

class Node(PlCoreBase):
    name = models.CharField(max_length=200, unique=True, help_text="Name of the Node")
    site  = models.ForeignKey(Site, related_name='nodes')
    deploymentNetwork  = models.ForeignKey(DeploymentNetwork, related_name='nodes')

    def __unicode__(self):  return u'%s' % (self.name)
