import os
import socket
from django.db import models
from core.models import PlCoreBase, Site, Slice, Sliver, Controller
from core.models import ControllerLinkManager,ControllerLinkDeletionManager
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.exceptions import ValidationError

# If true, then IP addresses will be allocated by the model. If false, then
# we will assume the observer handles it.
NO_OBSERVER=False

def ParseNatList(ports):
    """ Support a list of ports in the format "protocol:port, protocol:port, ..."
        examples:
            tcp 123
            tcp 123:133
            tcp 123, tcp 124, tcp 125, udp 201, udp 202

        User can put either a "/" or a " " between protocol and ports
        Port ranges can be specified with "-" or ":"
    """
    nats = []
    if ports:
        parts = ports.split(",")
        for part in parts:
            part = part.strip()
            if "/" in part:
                (protocol, ports) = part.split("/",1)
            elif " " in part:
                (protocol, ports) = part.split(None,1)
            else:
                raise TypeError('malformed port specifier %s, format example: "tcp 123, tcp 201:206, udp 333"' % part)

            protocol = protocol.strip()
            ports = ports.strip()

            if not (protocol in ["udp", "tcp"]):
                raise ValueError('unknown protocol %s' % protocol)

            if "-" in ports:
                (first, last) = ports.split("-")
                first = int(first.strip())
                last = int(last.strip())
                portStr = "%d:%d" % (first, last)
            elif ":" in ports:
                (first, last) = ports.split(":")
                first = int(first.strip())
                last = int(last.strip())
                portStr = "%d:%d" % (first, last)
            else:
                portStr = "%d" % int(ports)

            nats.append( {"l4_protocol": protocol, "l4_port": portStr} )

    return nats

def ValidateNatList(ports):
    try:
        ParseNatList(ports)
    except Exception,e:
        raise ValidationError(str(e))

class NetworkTemplate(PlCoreBase):
    VISIBILITY_CHOICES = (('public', 'public'), ('private', 'private'))
    TRANSLATION_CHOICES = (('none', 'none'), ('NAT', 'NAT'))
    TOPOLOGY_CHOICES = (('bigswitch', 'BigSwitch'), ('physical', 'Physical'), ('custom', 'Custom'))
    CONTROLLER_CHOICES = ((None, 'None'), ('onos', 'ONOS'), ('custom', 'Custom'))

    name = models.CharField(max_length=32)
    description = models.CharField(max_length=1024, blank=True, null=True)
    guaranteedBandwidth = models.IntegerField(default=0)
    visibility = models.CharField(max_length=30, choices=VISIBILITY_CHOICES, default="private")
    translation = models.CharField(max_length=30, choices=TRANSLATION_CHOICES, default="none")
    sharedNetworkName = models.CharField(max_length=30, blank=True, null=True)
    sharedNetworkId = models.CharField(null=True, blank=True, max_length=256, help_text="Quantum network")
    topologyKind = models.CharField(null=False, blank=False, max_length=30, choices=TOPOLOGY_CHOICES, default="BigSwitch")
    controllerKind = models.CharField(null=True, blank=True, max_length=30, choices=CONTROLLER_CHOICES, default=None)

    def __unicode__(self):  return u'%s' % (self.name)

class Network(PlCoreBase):
    name = models.CharField(max_length=32)
    template = models.ForeignKey(NetworkTemplate)
    subnet = models.CharField(max_length=32, blank=True)
    ports = models.CharField(max_length=1024, blank=True, null=True, validators=[ValidateNatList])
    labels = models.CharField(max_length=1024, blank=True, null=True)
    owner = models.ForeignKey(Slice, related_name="ownedNetworks", help_text="Slice that owns control of this Network")

    guaranteedBandwidth = models.IntegerField(default=0)
    permitAllSlices = models.BooleanField(default=False)
    permittedSlices = models.ManyToManyField(Slice, blank=True, related_name="availableNetworks")
    slices = models.ManyToManyField(Slice, blank=True, related_name="networks", through="NetworkSlice")
    slivers = models.ManyToManyField(Sliver, blank=True, related_name="networks", through="NetworkSliver")

    topologyParameters = models.TextField(null=True, blank=True)
    controllerUrl = models.CharField(null=True, blank=True, max_length=1024)
    controllerParameters = models.TextField(null=True, blank=True)

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

    def can_update(self, user):
        return self.owner.can_update(user)

    @property
    def nat_list(self):
        return ParseNatList(self.ports)

    @staticmethod
    def select_by_user(user):
        if user.is_admin:
            qs = Network.objects.all()
        else:
            slices = Slice.select_by_user(user)
            #slice_ids = [s.id for s in Slice.select_by_user(user)]
            qs = Network.objects.filter(owner__in=slices)
        return qs

class ControllerNetworks(PlCoreBase):
    objects = ControllerLinkManager()
    deleted_objects = ControllerLinkDeletionManager()

    # Stores the openstack ids at various controllers
    network = models.ForeignKey(Network, related_name='controllernetworks')
    controller = models.ForeignKey(Controller, related_name='controllernetworks')
    net_id = models.CharField(null=True, blank=True, max_length=256, help_text="Quantum network")
    router_id = models.CharField(null=True, blank=True, max_length=256, help_text="Quantum router id")
    subnet_id = models.CharField(null=True, blank=True, max_length=256, help_text="Quantum subnet id")
    subnet = models.CharField(max_length=32, blank=True)
       
    def can_update(self, user):
        return user.is_admin

    @staticmethod
    def select_by_user(user):
        if user.is_admin:
            qs = NetworkControllers.objects.all()
        else:
            slices = Slice.select_by_user(user)
            networks = Network.objects.filter(owner__in=slices)
            qs = NetworkControllers.objects.filter(network__in=networks)
        return qs

class NetworkSlice(PlCoreBase):
    # This object exists solely so we can implement the permission check when
    # adding slices to networks. It adds no additional fields to the relation.

    network = models.ForeignKey(Network,related_name='networkslices')
    slice = models.ForeignKey(Slice,related_name='networkslices')

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

    def can_update(self, user):
        return self.slice.can_update(user)

    @staticmethod
    def select_by_user(user):
        if user.is_admin:
            qs = NetworkSlice.objects.all()
        else:
            slice_ids = [s.id for s in Slice.select_by_user(user)]
            qs = NetworkSlice.objects.filter(id__in=slice_ids)
        return qs

class NetworkSliver(PlCoreBase):
    network = models.ForeignKey(Network,related_name='networkslivers')
    sliver = models.ForeignKey(Sliver,related_name='networkslivers')
    ip = models.GenericIPAddressField(help_text="Sliver ip address", blank=True, null=True)
    port_id = models.CharField(null=True, blank=True, max_length=256, help_text="Quantum port id")

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

    def can_update(self, user):
        return self.sliver.can_update(user)

    @staticmethod
    def select_by_user(user):
        if user.is_admin:
            qs = NetworkSliver.objects.all()
        else:
            sliver_ids = [s.id for s in NetworkSliver.select_by_user(user)]
            qs = NetworkSliver.objects.filter(id__in=sliver_ids)
        return qs

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
    parameter = models.ForeignKey(NetworkParameterType, related_name="networkparameters", help_text="The type of the parameter")
    value = models.CharField(help_text="The value of this parameter", max_length=1024)

    # The required fields to do a ObjectType lookup, and object_id assignment
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return self.parameter.name


