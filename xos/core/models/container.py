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
from monitor import driver as monitor
from django.core.exceptions import PermissionDenied, ValidationError

config = Config()


# Create your models here.
class Container(PlCoreBase):
    name = StrippedCharField(max_length=200, help_text="Container name")
    slice = models.ForeignKey(Slice, related_name='containers')
    node = models.ForeignKey(Node, related_name='containers')
    creator = models.ForeignKey(User, related_name='containers', blank=True, null=True)
    docker_image = StrippedCharField(null=True, blank=True, max_length=200, help_text="name of docker container to instantiate")

    def __unicode__(self):
        return u'container-%s' % str(self.id)

    def save(self, *args, **kwds):
        if not self.name:
            self.name = self.slice.name
        if not self.creator and hasattr(self, 'caller'):
            self.creator = self.caller
        if not self.creator:
            raise ValidationError('container has no creator')

        if (self.slice.creator != self.creator):
            # Check to make sure there's a slice_privilege for the user. If there
            # isn't, then keystone will throw an exception inside the observer.
            slice_privs = SlicePrivilege.objects.filter(slice=self.slice, user=self.creator)
            if not slice_privs:
                raise ValidationError('container creator has no privileges on slice')

# XXX smbaker - disabled for now, was causing fault in tenant view create slice
#        if not self.controllerNetwork.test_acl(slice=self.slice):
#            raise exceptions.ValidationError("Deployment %s's ACL does not allow any of this slice %s's users" % (self.controllerNetwork.name, self.slice.name))

        super(Container, self).save(*args, **kwds)

    def can_update(self, user):
        return True

    @staticmethod
    def select_by_user(user):
        if user.is_admin:
            qs = Container.objects.all()
        else:
            slices = Slice.select_by_user(user)
            qs = Container.objects.filter(slice__in=slices)
        return qs

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


