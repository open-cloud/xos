import os
from django.db import models
from django.core import exceptions
from core.models import PlCoreBase
from core.models import Image
from core.models import Slice
from core.models import Node
from core.models import Site
from core.models import Deployment
from core.models import User
from core.models import Tag
from django.contrib.contenttypes import generic

# Create your models here.
class Sliver(PlCoreBase):
    instance_id = models.CharField(null=True, blank=True, max_length=200, help_text="Nova instance id")    
    name = models.CharField(max_length=200, help_text="Sliver name")
    instance_name = models.CharField(blank=True, null=True, max_length=200, help_text="OpenStack generated name")
    ip = models.GenericIPAddressField(help_text="Sliver ip address", blank=True, null=True)
    image = models.ForeignKey(Image, related_name='slivers')
    #key = models.ForeignKey(Key, related_name='slivers')
    creator = models.ForeignKey(User, related_name='slivers', blank=True, null=True)
    slice = models.ForeignKey(Slice, related_name='slivers')
    node = models.ForeignKey(Node, related_name='slivers')
    deploymentNetwork = models.ForeignKey(Deployment, verbose_name='deployment', related_name='sliver_deploymentNetwork')
    numberCores = models.IntegerField(verbose_name="Number of Cores", help_text="Number of cores for sliver", default=0)
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
        if not self.name:
            self.name = self.slice.name
        if not self.creator and hasattr(self, 'caller'):
            self.creator = self.caller
        self.deploymentNetwork = self.node.deployment

# XXX smbaker - disabled for now, was causing fault in tenant view create slice
#        if not self.deploymentNetwork.test_acl(slice=self.slice):
#            raise exceptions.ValidationError("Deployment %s's ACL does not allow any of this slice %s's users" % (self.deploymentNetwork.name, self.slice.name))

        super(Sliver, self).save(*args, **kwds)

    def can_update(self, user):
        return self.slice.can_update(user)

    @staticmethod
    def select_by_user(user):
        if user.is_admin:
            qs = Sliver.objects.all()
        else:
            slices = Slice.select_by_user(user)
            qs = Sliver.objects.filter(slice__in=slices)
        return qs
