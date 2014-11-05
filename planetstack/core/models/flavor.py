import os
import socket
from django.db import models
from core.models import PlCoreBase, Deployment
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

class Flavor(PlCoreBase):
    name = models.CharField(max_length=32, help_text="name of this flavor, as displayed to users")
    description = models.CharField(max_length=1024, blank=True, null=True)
    flavor = models.CharField(max_length=32, help_text="flavor string used to configure deployments")
    deployments = models.ManyToManyField(Deployment, blank=True, related_name="flavors")
    order = models.IntegerField(default=0, help_text="used to order flavors when displayed in a list")
    default = models.BooleanField(default=False, help_text="make this a default flavor to use when creating new instances")

    class Meta:
        app_label = "core"
        ordering = ('order', 'name')

    def __unicode__(self):  return u'%s' % (self.name)

""" FlavorParameterType and FlavorParameter are below for completeness sake,
    waiting for the day we might want to add parameters to flavors.

class FlavorParameterType(PlCoreBase):
    name = models.SlugField(help_text="The name of this parameter", max_length=128)
    description = models.CharField(max_length=1024)

    def __unicode__(self):  return u'%s' % (self.name)

class FlavorParameter(PlCoreBase):
    parameter = models.ForeignKey(FlavorParameterType, related_name="parameters", help_text="The type of the parameter")
    value = models.CharField(help_text="The value of this parameter", max_length=1024)

    flavor = models.ForeignKey(Flavor,related_name='flavorparameter')

    def __unicode__(self):
        return self.parameter.name

"""

