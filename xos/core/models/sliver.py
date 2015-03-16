import os
from django.db import models
from django.db.models import Q
from django.core import exceptions
from core.models import PlCoreBase,PlCoreBaseManager,PlCoreBaseDeletionManager
from core.models.plcorebase import StrippedCharField
from core.models import Image
from core.models import Slice
from core.models import Node
from core.models import Site
from core.models import Deployment
from core.models import Controller
from core.models import User
from core.models import Tag
from core.models import Flavor
from django.contrib.contenttypes import generic
from xos.config import Config
from monitor import driver as monitor

config = Config()

def get_default_flavor(controller = None):
    # Find a default flavor that can be used for a sliver. This is particularly
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

class SliverDeletionManager(PlCoreBaseDeletionManager):
    def get_queryset(self):
        parent=super(SliverDeletionManager, self)
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


class SliverManager(PlCoreBaseManager):
    def get_queryset(self):
        parent=super(SliverManager, self)

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
class Sliver(PlCoreBase):
    objects = SliverManager()
    deleted_objects = SliverDeletionManager()
    instance_id = StrippedCharField(null=True, blank=True, max_length=200, help_text="Nova instance id")
    instance_uuid = StrippedCharField(null=True, blank=True, max_length=200, help_text="Nova instance uuid")
    name = StrippedCharField(max_length=200, help_text="Sliver name")
    instance_name = StrippedCharField(blank=True, null=True, max_length=200, help_text="OpenStack generated name")
    ip = models.GenericIPAddressField(help_text="Sliver ip address", blank=True, null=True)
    image = models.ForeignKey(Image, related_name='slivers')
    #key = models.ForeignKey(Key, related_name='slivers')
    creator = models.ForeignKey(User, related_name='slivers', blank=True, null=True)
    slice = models.ForeignKey(Slice, related_name='slivers')
    deployment = models.ForeignKey(Deployment, verbose_name='deployment', related_name='sliver_deployment')
    node = models.ForeignKey(Node, related_name='slivers')
    numberCores = models.IntegerField(verbose_name="Number of Cores", help_text="Number of cores for sliver", default=0)
    flavor = models.ForeignKey(Flavor, help_text="Flavor of this instance", default=get_default_flavor)
    tags = generic.GenericRelation(Tag)
    userData = models.TextField(blank=True, null=True, help_text="user_data passed to instance during creation")

    def __unicode__(self):
        if self.instance_name:
            return u'%s' % (self.instance_name)
        elif self.id:
            return u'uninstantiated-%s' % str(self.id)
        elif self.slice:
            return u'unsaved-sliver on %s' % self.slice.name
        else:
            return u'unsaved-sliver'

    def save(self, *args, **kwds):
        self.name = self.slice.name
        if not self.creator and hasattr(self, 'caller'):
            self.creator = self.caller
        if not self.creator:
            raise ValidationError('sliver has no creator')

# XXX smbaker - disabled for now, was causing fault in tenant view create slice
#        if not self.controllerNetwork.test_acl(slice=self.slice):
#            raise exceptions.ValidationError("Deployment %s's ACL does not allow any of this slice %s's users" % (self.controllerNetwork.name, self.slice.name))

        super(Sliver, self).save(*args, **kwds)

    def can_update(self, user):
        return user.can_update_slice(self.slice)

    def all_ips(self):
        ips={}
        for ns in self.networkslivers.all():
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

    def get_public_ip(self, sliver):
        for ns in self.networkslivers.all():
            if (ns.ip) and (ns.network.template.visibility=="public") and (ns.network.template.translation=="none"):
                return ns.ip
        return None

    @staticmethod
    def select_by_user(user):
        if user.is_admin:
            qs = Sliver.objects.all()
        else:
            slices = Slice.select_by_user(user)
            qs = Sliver.objects.filter(slice__in=slices)
        return qs

    def get_cpu_stats(self):
        filter = 'instance_id=%s'%self.sliver_id
        return monitor.get_meter('cpu',filter,None)

    def get_bw_stats(self):
        filter = 'instance_id=%s'%self.sliver_id
        return monitor.get_meter('network.outgoing.bytes',filter,None)

    def get_node_stats(self):
        # Note sure what should go back here
        return 1

    def get_ssh_command(self):
        if (not self.instance_id) or (not self.node) or (not self.instance_name):
            return None
        else:
            return 'ssh -o "ProxyCommand ssh -q %s@%s" ubuntu@%s' % (self.instance_id, self.node.name, self.instance_name)
