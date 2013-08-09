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
    TRANSLATION_CHOICES = (('none', 'none'), ('NAT', 'NAT'))

    name = models.CharField(max_length=32)
    description = models.CharField(max_length=1024, blank=True, null=True)
    guaranteedBandwidth = models.IntegerField(default=0)
    visibility = models.CharField(max_length=30, choices=VISIBILITY_CHOICES, default="private")
    translation = models.CharField(max_length=30, choices=TRANSLATION_CHOICES, default="none")
    sharedNetworkName = models.CharField(max_length=30, blank=True, null=True)
    sharedNetworkId = models.CharField(null=True, blank=True, max_length=256, help_text="Quantum network")

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
    slices = models.ManyToManyField(Slice, blank=True, related_name="networks", through="NetworkSlice")
    slivers = models.ManyToManyField(Sliver, blank=True, related_name="networks", through="NetworkSliver")

    # for observer/manager
    network_id = models.CharField(null=True, blank=True, max_length=256, help_text="Quantum network")
    router_id = models.CharField(null=True, blank=True, max_length=256, help_text="Quantum router id")
    subnet_id = models.CharField(null=True, blank=True, max_length=256, help_text="Quantum subnet id")

    def __unicode__(self):  return u'%s' % (self.name)

    def save(self, *args, **kwds):
        if (not self.subnet) and (NO_OBSERVER):
            from util.network_subnet_allocator import find_unused_subnet
            self.subnet = find_unused_subnet(existing_subnets=[x.subnet for x in Network.objects.all()])
        super(Network, self).save(*args, **kwds)

class NetworkSlice(PlCoreBase):
    # This object exists solely so we can implement the permission check when
    # adding slices to networks. It adds no additional fields to the relation.

    network = models.ForeignKey(Network)
    slice = models.ForeignKey(Slice)

    def save(self, *args, **kwds):
        slice = self.slice
        if (slice not in self.network.permittedSlices.all()) and (slice != self.network.owner) and (not self.network.permitAllSlices):
            # to add a sliver to the network, then one of the following must be true:
            #   1) sliver's slice is in network's permittedSlices list,
            #   2) sliver's slice is network's owner, or
            #   3) network's permitAllSlices is true
            raise ValueError("Slice %s is not allowed to connect to network %s" % (str(slice), str(self.network)))

        super(NetworkSlice, self).save(*args, **kwds)

    def __unicode__(self):  return u'%s-%s' % (self.network.name, self.slice.name)

class NetworkSliver(PlCoreBase):
    network = models.ForeignKey(Network)
    sliver = models.ForeignKey(Sliver)
    ip = models.GenericIPAddressField(help_text="Sliver ip address", blank=True, null=True)

    def save(self, *args, **kwds):
        slice = self.sliver.slice
        if (slice not in self.network.permittedSlices.all()) and (slice != self.network.owner) and (not self.network.permitAllSlices):
            # to add a sliver to the network, then one of the following must be true:
            #   1) sliver's slice is in network's permittedSlices list,
            #   2) sliver's slice is network's owner, or
            #   3) network's permitAllSlices is true
            raise ValueError("Slice %s is not allowed to connect to network %s" % (str(slice), str(self.network)))

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


