import os
import socket
from django.db import models
from core.models import PlCoreBase, Site, Slice, Sliver
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

# If true, then IP addresses will be allocated by the model. If false, then
# we will assume the observer handles it.
NO_OBSERVER=False

class NetworkTemplate(PlCoreBase):
    VISIBILITY_CHOICES = (('public', 'public'), ('private', 'private'))

    name = models.CharField(max_length=32)
    description = models.CharField(max_length=1024, blank=True, null=True)
    guaranteedBandwidth = models.IntegerField(default=0)
    visibility = models.CharField(max_length=30, choices=VISIBILITY_CHOICES, default="private")

    def __unicode__(self):  return u'%s' % (self.name)

class Network(PlCoreBase):
    name = models.CharField(max_length=32)
    template = models.ForeignKey(NetworkTemplate)
    subnet = models.CharField(max_length=32, blank=True)
    ports = models.CharField(max_length=1024, blank=True, null=True)
    labels = models.CharField(max_length=1024, blank=True, null=True)
    owner = models.ForeignKey(Slice, related_name="ownedNetworks")

    guaranteedBandwidth = models.IntegerField(default=0)
    permitAllSlices = models.BooleanField(default=False)
    permittedSlices = models.ManyToManyField(Slice, blank=True, related_name="availableNetworks")
    slices = models.ManyToManyField(Slice, blank=True, related_name="networks")
    slivers = models.ManyToManyField(Sliver, blank=True, related_name="networks", through="NetworkSliver")

    def __unicode__(self):  return u'%s' % (self.name)

    def save(self, *args, **kwds):
        if (not self.subnet) and (NO_OBSERVER):
            from util.network_subnet_allocator import find_unused_subnet
            self.subnet = find_unused_subnet(existing_subnets=[x.subnet for x in Network.objects.all()])
        super(Network, self).save(*args, **kwds)

class NetworkSliver(PlCoreBase):
    network = models.ForeignKey(Network)
    sliver = models.ForeignKey(Sliver)
    ip = models.GenericIPAddressField(help_text="Sliver ip address", blank=True, null=True)

    def save(self, *args, **kwds):
        if (not self.ip) and (NO_OBSERVER):
            from util.network_subnet_allocator import find_unused_address
            self.ip = find_unused_address(self.network.subnet,
                                          [x.ip for x in self.network.networksliver_set.all()])
        super(NetworkSliver, self).save(*args, **kwds)

    def __unicode__(self):  return u'%s-%s' % (self.network.name, self.sliver.instance_name)

class Router(PlCoreBase):
    name = models.CharField(max_length=32)
    owner = models.ForeignKey(Slice, related_name="routers")
    permittedNetworks = models.ManyToManyField(Network, blank=True, related_name="availableRouters")
    networks = models.ManyToManyField(Network, blank=True, related_name="routers")

    def __unicode__(self):  return u'%s' % (self.name)

class NetworkParameterType(PlCoreBase):
    name = models.SlugField(help_text="The name of this parameter", max_length=128)
    description = models.CharField(max_length=1024)

    def __unicode__(self):  return u'%s' % (self.name)

class NetworkParameter(PlCoreBase):
    parameter = models.ForeignKey(NetworkParameterType, related_name="parameters", help_text="The type of the parameter")
    value = models.CharField(help_text="The value of this parameter", max_length=1024)

    # The required fields to do a ObjectType lookup, and object_id assignment
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return self.parameter.name


