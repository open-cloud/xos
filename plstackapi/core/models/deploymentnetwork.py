import os
from django.db import models
from plstackapi.core.models import PlCoreBase

# Create your models here.

class DeploymentNetwork(PlCoreBase):
    name = models.CharField(max_length=200, unique=True, help_text="Name of the Deployment Network")

    def __unicode__(self):  return u'%s' % (self.name)

