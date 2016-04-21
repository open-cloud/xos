import os
import socket
import sys
from django.db import models, transaction
from core.models import PlCoreBase, Site, Slice, Instance, Controller, Service
from core.models import ControllerLinkManager,ControllerLinkDeletionManager
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.exceptions import ValidationError
from django.db.models import Q

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

class ParameterMixin(object):
    # helper classes for dealing with NetworkParameter

    def get_parameters(self):
        parameter_dict = {}

        instance_type = ContentType.objects.get_for_model(self)
        for param in NetworkParameter.objects.filter(content_type__pk=instance_type.id, object_id=self.id):
            parameter_dict[param.parameter.name] = param.value

        return parameter_dict

    def set_parameter(self, name, value):
        instance_type = ContentType.objects.get_for_model(self)
        existing_params = NetworkParameter.objects.filter(parameter__name=name, content_type__pk=instance_type.id, object_id=self.id)
        if existing_params:
            p=existing_params[0]
            p.value = value
            p.save()
        else:
            pt = NetworkParameterType.objects.get(name=name)
            p = NetworkParameter(parameter=pt, content_type=instance_type, object_id=self.id, value=value)
            p.save()

    def unset_parameter(self, name):
        instance_type = ContentType.objects.get_for_model(self)
        existing_params = NetworkParameter.objects.filter(parameter__name=name, content_type__pk=instance_type.id, object_id=self.id)
        for p in existing_params:
            p.delete()


class NetworkTemplate(PlCoreBase, ParameterMixin):
    VISIBILITY_CHOICES = (('public', 'public'), ('private', 'private'))
    TRANSLATION_CHOICES = (('none', 'none'), ('NAT', 'NAT'))
    TOPOLOGY_CHOICES = (('bigswitch', 'BigSwitch'), ('physical', 'Physical'), ('custom', 'Custom'))
    CONTROLLER_CHOICES = ((None, 'None'), ('onos', 'ONOS'), ('custom', 'Custom'))
    ACCESS_CHOICES = ((None, 'None'), ('indirect', 'Indirect'), ('direct', 'Direct'))

    name = models.CharField(max_length=32)
    description = models.CharField(max_length=1024, blank=True, null=True)
    guaranteed_bandwidth = models.IntegerField(default=0)
    visibility = models.CharField(max_length=30, choices=VISIBILITY_CHOICES, default="private")
    translation = models.CharField(max_length=30, choices=TRANSLATION_CHOICES, default="none")
    access = models.CharField(max_length=30, null=True, blank=True, choices=ACCESS_CHOICES, help_text="Advertise this network as a means for other slices to contact this slice")
    shared_network_name = models.CharField(max_length=30, blank=True, null=True)
    shared_network_id = models.CharField(null=True, blank=True, max_length=256, help_text="Quantum network")
    topology_kind = models.CharField(null=False, blank=False, max_length=30, choices=TOPOLOGY_CHOICES, default="bigswitch")
    controller_kind = models.CharField(null=True, blank=True, max_length=30, choices=CONTROLLER_CHOICES, default=None)

    def __init__(self, *args, **kwargs):
        super(NetworkTemplate, self).__init__(*args, **kwargs)

        # somehow these got set wrong inside of the live database. Remove this
        # code after all is well...
        if (self.topology_kind=="BigSwitch"):
            print >> sys.stderr, "XXX warning: topology_kind invalid case"
            self.topology_kind="bigswitch"
        elif (self.topology_kind=="Physical"):
            print >> sys.stderr, "XXX warning: topology_kind invalid case"
            self.topology_kind="physical"
        elif (self.topology_kind=="Custom"):
            print >> sys.stderr, "XXX warning: topology_kind invalid case"
            self.toplogy_kind="custom"

    def save(self, *args, **kwargs):
        self.enforce_choices(self.access, self.ACCESS_CHOICES)
        super(NetworkTemplate, self).save(*args, **kwargs)

    def __unicode__(self):  return u'%s' % (self.name)

class Network(PlCoreBase, ParameterMixin):
    name = models.CharField(max_length=32)
    template = models.ForeignKey(NetworkTemplate)
    subnet = models.CharField(max_length=32, blank=True)
    start_ip = models.CharField(max_length=32, blank=True)
    end_ip = models.CharField(max_length=32, blank=True)
    ports = models.CharField(max_length=1024, blank=True, null=True, validators=[ValidateNatList])
    labels = models.CharField(max_length=1024, blank=True, null=True)
    owner = models.ForeignKey(Slice, related_name="ownedNetworks", help_text="Slice that owns control of this Network")

    guaranteed_bandwidth = models.IntegerField(default=0)
    permit_all_slices = models.BooleanField(default=False)
    permitted_slices = models.ManyToManyField(Slice, blank=True, related_name="availableNetworks")
    slices = models.ManyToManyField(Slice, blank=True, related_name="networks", through="NetworkSlice")
    instances = models.ManyToManyField(Instance, blank=True, related_name="networks", through="Port")

    topology_parameters = models.TextField(null=True, blank=True)
    controller_url = models.CharField(null=True, blank=True, max_length=1024)
    controller_parameters = models.TextField(null=True, blank=True)

    # for observer/manager
    network_id = models.CharField(null=True, blank=True, max_length=256, help_text="Quantum network")
    router_id = models.CharField(null=True, blank=True, max_length=256, help_text="Quantum router id")
    subnet_id = models.CharField(null=True, blank=True, max_length=256, help_text="Quantum subnet id")

    autoconnect = models.BooleanField(default=True, help_text="This network can be autoconnected to the slice that owns it")

    def __unicode__(self):  return u'%s' % (self.name)

    def save(self, *args, **kwds):
        if (not self.subnet) and (NO_OBSERVER):
            from util.network_subnet_allocator import find_unused_subnet
            self.subnet = find_unused_subnet(existing_subnets=[x.subnet for x in Network.objects.all()])
            print "DEF_MOD_NET_IP", self.start_ip
        super(Network, self).save(*args, **kwds)

    def can_update(self, user):
        return user.can_update_slice(self.owner)

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

    def get_parameters(self):
        # returns parameters from the template, updated by self.
        p={}
        if self.template:
            p = self.template.get_parameters()
        p.update(ParameterMixin.get_parameters(self))
        return p

class ControllerNetwork(PlCoreBase):
    objects = ControllerLinkManager()
    deleted_objects = ControllerLinkDeletionManager()

    # Stores the openstack ids at various controllers
    network = models.ForeignKey(Network, related_name='controllernetworks')
    controller = models.ForeignKey(Controller, related_name='controllernetworks')
    net_id = models.CharField(null=True, blank=True, max_length=256, help_text="Quantum network")
    router_id = models.CharField(null=True, blank=True, max_length=256, help_text="Quantum router id")
    subnet_id = models.CharField(null=True, blank=True, max_length=256, help_text="Quantum subnet id")
    subnet = models.CharField(max_length=32, blank=True)
    start_ip = models.CharField(max_length=32, blank=True)
    stop_ip = models.CharField(max_length=32, blank=True)

    class Meta:
        unique_together = ('network', 'controller')

    def tologdict(self):
        d=super(ControllerNetwork,self).tologdict()
        try:
            d['network_name']=self.network.name
            d['controller_name']=self.controller.name
        except:
            pass
        return d
 
    @staticmethod
    def select_by_user(user):
        if user.is_admin:
            qs = ControllerNetwork.objects.all()
        else:
            slices = Slice.select_by_user(user)
            networks = Network.objects.filter(owner__in=slices)
            qs = ControllerNetwork.objects.filter(network__in=networks)
        return qs

class NetworkSlice(PlCoreBase):
    # This object exists solely so we can implement the permission check when
    # adding slices to networks. It adds no additional fields to the relation.

    network = models.ForeignKey(Network,related_name='networkslices')
    slice = models.ForeignKey(Slice,related_name='networkslices')

    class Meta:
        unique_together = ('network', 'slice')

    def save(self, *args, **kwds):
        slice = self.slice
        if (slice not in self.network.permitted_slices.all()) and (slice != self.network.owner) and (not self.network.permit_all_slices):
            # to add a instance to the network, then one of the following must be true:
            #   1) instance's slice is in network's permittedSlices list,
            #   2) instance's slice is network's owner, or
            #   3) network's permitAllSlices is true
            raise ValueError("Slice %s is not allowed to connect to network %s" % (str(slice), str(self.network)))

        super(NetworkSlice, self).save(*args, **kwds)

    def __unicode__(self):  return u'%s-%s' % (self.network.name, self.slice.name)

    def can_update(self, user):
        return user.can_update_slice(self.slice)

    @staticmethod
    def select_by_user(user):
        if user.is_admin:
            qs = NetworkSlice.objects.all()
        else:
            slice_ids = [s.id for s in Slice.select_by_user(user)]
            network_ids = [network.id for network in Network.select_by_user(user)]
            qs = NetworkSlice.objects.filter(Q(slice__in=slice_ids) | Q(network__in=network_ids))
        return qs

class Port(PlCoreBase, ParameterMixin):
    network = models.ForeignKey(Network,related_name='links')
    instance = models.ForeignKey(Instance, null=True, blank=True, related_name='ports')
    ip = models.GenericIPAddressField(help_text="Instance ip address", blank=True, null=True)
    port_id = models.CharField(null=True, blank=True, max_length=256, help_text="Neutron port id")
    mac = models.CharField(null=True, blank=True, max_length=256, help_text="MAC address associated with this port")
    xos_created = models.BooleanField(default=False) # True if XOS created this port in Neutron, False if port created by Neutron and observed by XOS

    class Meta:
        unique_together = ('network', 'instance')

    def save(self, *args, **kwds):
        if self.instance:
            slice = self.instance.slice
            if (slice not in self.network.permitted_slices.all()) and (slice != self.network.owner) and (not self.network.permit_all_slices):
                # to add a instance to the network, then one of the following must be true:
                #   1) instance's slice is in network's permittedSlices list,
                #   2) instance's slice is network's owner, or
                #   3) network's permitAllSlices is true
                raise ValueError("Slice %s is not allowed to connect to network %s" % (str(slice), str(self.network)))

        super(Port, self).save(*args, **kwds)

    def __unicode__(self):
        if self.instance:
            return u'%s-%s' % (self.network.name, self.instance.instance_name)
        else:
            return u'%s-unboundport-%s' % (self.network.name, self.id)

    def can_update(self, user):
        if self.instance:
            return user.can_update_slice(self.instance.slice)
        if self.network:
            return user.can_update_slice(self.network.owner)
        return False

    @staticmethod
    def select_by_user(user):
        if user.is_admin:
            qs = Port.objects.all()
        else:
            instances = Instance.select_by_user(user)
            instance_ids = [instance.id for instance in instances]
            networks = Network.select_by_user(user)
            network_ids = [network.id for network in networks]
            qs = Port.objects.filter(Q(instance__in=instance_ids) | Q(network__in=network_ids))
        return qs

    def get_parameters(self):
        # returns parameters from the network, updated by self.
        p={}
        if self.network:
            p = self.network.get_parameters()
        p.update(ParameterMixin.get_parameters(self))
        return p

class Router(PlCoreBase):
    name = models.CharField(max_length=32)
    owner = models.ForeignKey(Slice, related_name="routers")
    permittedNetworks = models.ManyToManyField(Network, blank=True, related_name="availableRouters")
    networks = models.ManyToManyField(Network, blank=True, related_name="routers")

    def __unicode__(self):  return u'%s' % (self.name)

    def can_update(self, user):
        return user.can_update_slice(self.owner)

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

class AddressPool(PlCoreBase):
    name = models.CharField(max_length=32)
    addresses = models.TextField(blank=True, null=True)
    gateway_ip = models.CharField(max_length=32, null=True)
    gateway_mac = models.CharField(max_length=32, null=True)
    cidr = models.CharField(max_length=32, null=True)
    inuse = models.TextField(blank=True, null=True)
    service = models.ForeignKey(Service, related_name="addresspools", null=True, blank=True)

    def __unicode__(self): return u'%s' % (self.name)

    def get_address(self):
        with transaction.atomic():
            ap = AddressPool.objects.get(pk=self.pk)
            if ap.addresses:
                avail_ips = ap.addresses.split()
            else:
                avail_ips = []

            if ap.inuse:
                inuse_ips = ap.inuse.split()
            else:
                inuse_ips = []

            while avail_ips:
                addr = avail_ips.pop(0)

                if addr in inuse_ips:
                    # This may have happened if someone re-ran the tosca
                    # recipe and 'refilled' the AddressPool while some addresses
                    # were still in use.
                    continue

                inuse_ips.insert(0,addr)

                ap.inuse = " ".join(inuse_ips)
                ap.addresses = " ".join(avail_ips)
                ap.save()
                return addr

            addr = None
        return addr

    def put_address(self, addr):
        with transaction.atomic():
            ap = AddressPool.objects.get(pk=self.pk)
            addresses = ap.addresses or ""
            parts = addresses.split()
            if addr not in parts:
                parts.insert(0,addr)
                ap.addresses = " ".join(parts)

            inuse = ap.inuse or ""
            parts = inuse.split()
            if addr in parts:
                parts.remove(addr)
                ap.inuse = " ".join(parts)

            ap.save()


