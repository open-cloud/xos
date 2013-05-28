import os
from django.db import models
from core.models import PlCoreBase
from core.models import Site
from core.models import Deployment

# Create your models here.

class Node(PlCoreBase):
    name = models.CharField(max_length=200, unique=True, help_text="Name of the Node")
    site  = models.ForeignKey(Site, related_name='nodes')
    deployment = models.ForeignKey(Deployment, related_name='nodes')

    def __unicode__(self):  return u'%s' % (self.name)
