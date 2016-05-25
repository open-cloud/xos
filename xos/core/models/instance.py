import os
from django.db import models
from django.db.models import Q
from django.core import exceptions
from core.models import PlCoreBase,PlCoreBaseManager,PlCoreBaseDeletionManager
from core.models.plcorebase import StrippedCharField
from core.models import Image
from core.models import Slice, SlicePrivilege
from core.models import Node
from core.models import Site
from core.models import Deployment
from core.models import Controller
from core.models import User
from core.models import Tag
from core.models import Flavor
from django.contrib.contenttypes import generic
from xos.config import Config
from django.core.exceptions import PermissionDenied, ValidationError

config = Config()

def get_default_flavor(controller = None):
    # Find a default flavor that can be used for a instance. This is particularly
    # useful in evolution. It's also intended this helper function can be used
    # for admin.py when users

    if controller:
        flavors = controller.flavors.all()
    else:
        flavors = Flavor.objects.all()

    if not flavors:
        return None

    for flavor in flavors:
        if flavor.default:
            return flavor

    return flavors[0]

class InstanceDeletionManager(PlCoreBaseDeletionManager):
    def get_queryset(self):
        parent=super(InstanceDeletionManager, self)
        try:
            backend_type = config.observer_backend_type
        except AttributeError:
            backend_type = None

        parent_queryset = parent.get_queryset() if hasattr(parent, "get_queryset") else parent.get_query_set()
        if (backend_type):
            return parent_queryset.filter(Q(node__controller__backend_type=backend_type))
        else:
            return parent_queryset

    # deprecated in django 1.7 in favor of get_queryset().
    def get_query_set(self):
        return self.get_queryset()


class InstanceManager(PlCoreBaseManager):
    def get_queryset(self):
        parent=super(InstanceManager, self)

        try:
            backend_type = config.observer_backend_type
        except AttributeError:
            backend_type = None

        parent_queryset = parent.get_queryset() if hasattr(parent, "get_queryset") else parent.get_query_set()

        if backend_type:
            return parent_queryset.filter(Q(node__controller__backend_type=backend_type))
        else:
            return parent_queryset

    # deprecated in django 1.7 in favor of get_queryset().
    def get_query_set(self):
        return self.get_queryset()

# Create your models here.
class Instance(PlCoreBase):
    ISOLATION_CHOICES = (('vm', 'Virtual Machine'), ('container', 'Container'), ('container_vm', 'Container In VM'))

    objects = InstanceManager()
    deleted_objects = InstanceDeletionManager()
    instance_id = StrippedCharField(null=True, blank=True, max_length=200, help_text="Nova instance id")
    instance_uuid = StrippedCharField(null=True, blank=True, max_length=200, help_text="Nova instance uuid")
    name = StrippedCharField(max_length=200, help_text="Instance name")
    instance_name = StrippedCharField(blank=True, null=True, max_length=200, help_text="OpenStack generated name")
    ip = models.GenericIPAddressField(help_text="Instance ip address", blank=True, null=True)
    image = models.ForeignKey(Image, related_name='instances')
    creator = models.ForeignKey(User, related_name='instances', blank=True, null=True)
    slice = models.ForeignKey(Slice, related_name='instances')
    deployment = models.ForeignKey(Deployment, verbose_name='deployment', related_name='instance_deployment')
    node = models.ForeignKey(Node, related_name='instances')
    numberCores = models.IntegerField(verbose_name="Number of Cores", help_text="Number of cores for instance", default=0)
    flavor = models.ForeignKey(Flavor, help_text="Flavor of this instance", default=get_default_flavor)
    tags = generic.GenericRelation(Tag)
    userData = models.TextField(blank=True, null=True, help_text="user_data passed to instance during creation")
    isolation = models.CharField(null=False, blank=False, max_length=30, choices=ISOLATION_CHOICES, default="vm")
    volumes = models.TextField(null=True, blank=True, help_text="Comma-separated list of directories to expose to parent context")
    parent = models.ForeignKey("Instance", null=True, blank=True, help_text="Parent Instance for containers nested inside of VMs")

    def get_controller (self):
        return self.node.site_deployment.controller

    def tologdict(self):
        d=super(Instance,self).tologdict()
        try:
            d['slice_name']=self.slice.name
            d['controller_name']=self.get_controller().name
        except:
            pass
        return d

    def __unicode__(self):
        if self.name and Slice.objects.filter(id=self.slice_id) and (self.name != self.slice.name):
            # NOTE: The weird check on self.slice_id was due to a problem when
            #   deleting the slice before the instance.
            return u'%s' % self.name
        elif self.instance_name:
            return u'%s' % (self.instance_name)
        elif self.id:
            return u'uninstantiated-%s' % str(self.id)
        elif self.slice:
            return u'unsaved-instance on %s' % self.slice.name
        else:
            return u'unsaved-instance'

    def save(self, *args, **kwds):
        if not self.name:
            self.name = self.slice.name
        if not self.creator and hasattr(self, 'caller'):
            self.creator = self.caller
        if not self.creator:
            raise ValidationError('instance has no creator')

        if (self.isolation == "container") or (self.isolation == "container_vm"):
            if (self.image.kind != "container"):
               raise ValidationError("Container instance must use container image")
        elif (self.isolation == "vm"):
            if (self.image.kind != "vm"):
               raise ValidationError("VM instance must use VM image")

        if (self.isolation == "container_vm") and (not self.parent):
            raise ValidationError("Container-vm instance must have a parent")

        if (self.parent) and (self.isolation != "container_vm"):
            raise ValidationError("Parent field can only be set on Container-vm instances")

        if (self.slice.creator != self.creator):
            # Check to make sure there's a slice_privilege for the user. If there
            # isn't, then keystone will throw an exception inside the observer.
            slice_privs = SlicePrivilege.objects.filter(slice=self.slice, user=self.creator)
            if not slice_privs:
                raise ValidationError('instance creator has no privileges on slice')

# XXX smbaker - disabled for now, was causing fault in tenant view create slice
#        if not self.controllerNetwork.test_acl(slice=self.slice):
#            raise exceptions.ValidationError("Deployment %s's ACL does not allow any of this slice %s's users" % (self.controllerNetwork.name, self.slice.name))

        super(Instance, self).save(*args, **kwds)

    def can_update(self, user):
        return user.can_update_slice(self.slice)

    def all_ips(self):
        ips={}
        for ns in self.ports.all():
           if ns.ip:
               ips[ns.network.name] = ns.ip
        return ips

    def all_ips_string(self):
        result = []
        ips = self.all_ips()
        for key in sorted(ips.keys()):
            #result.append("%s = %s" % (key, ips[key]))
            result.append(ips[key])
        return ", ".join(result)
    all_ips_string.short_description = "addresses"

    def get_public_ip(self):
        for ns in self.ports.all():
            if (ns.ip) and (ns.network.template.visibility=="public") and (ns.network.template.translation=="none"):
                return ns.ip
        return None

    # return an address on nat-net
    def get_network_ip(self, pattern):
        for ns in self.ports.all():
            if pattern in ns.network.name.lower():
                return ns.ip
        return None

    # return an address that the synchronizer can use to SSH to the instance
    def get_ssh_ip(self):
        management=self.get_network_ip("management")
        if management:
            return management
        return self.get_network_ip("nat")

    @staticmethod
    def select_by_user(user):
        if user.is_admin:
            qs = Instance.objects.all()
        else:
            slices = Slice.select_by_user(user)
            qs = Instance.objects.filter(slice__in=slices)
        return qs

    def get_cpu_stats(self):
        filter = 'instance_id=%s'%self.instance_id
        return monitor.get_meter('cpu',filter,None)

    def get_bw_stats(self):
        filter = 'instance_id=%s'%self.instance_id
        return monitor.get_meter('network.outgoing.bytes',filter,None)

    def get_node_stats(self):
        # Note sure what should go back here
        return 1

    def get_ssh_command(self):
        if (not self.instance_id) or (not self.node) or (not self.instance_name):
            return None
        else:
            return 'ssh -o "ProxyCommand ssh -q %s@%s" ubuntu@%s' % (self.instance_id, self.node.name, self.instance_name)

    def get_public_keys(self):
        slice_memberships = SlicePrivilege.objects.filter(slice=self.slice)
        pubkeys = set([sm.user.public_key for sm in slice_memberships if sm.user.public_key])

        if self.creator.public_key:
            pubkeys.add(self.creator.public_key)

        if self.slice.creator.public_key:
            pubkeys.add(self.slice.creator.public_key)

        if self.slice.service and self.slice.service.public_key:
            pubkeys.add(self.slice.service.public_key)

        return pubkeys

def controller_setter(instance, **kwargs):
    try:
        instance.controller = instance.node.site_deployment.controller
    except:
        instance.controller = None

models.signals.post_init.connect(controller_setter, Instance)
