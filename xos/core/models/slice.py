import os
from django.db import models
from core.models import PlCoreBase
from core.models import Site
from core.models.site import SitePrivilege
from core.models import User
from core.models import Role
from core.models import Controller,ControllerLinkManager,ControllerLinkDeletionManager
from core.models import ServiceClass
from core.models.serviceclass import get_default_serviceclass
from core.models import Tag
from django.contrib.contenttypes import generic
from core.models import Service
from core.models import Controller
from core.models import Flavor, Image
from core.models.plcorebase import StrippedCharField
from django.core.exceptions import PermissionDenied, ValidationError

# Create your models here.

class Slice(PlCoreBase):
    name = StrippedCharField(unique=True, help_text="The Name of the Slice", max_length=80)
    enabled = models.BooleanField(default=True, help_text="Status for this Slice")
    omf_friendly = models.BooleanField(default=False)
    description=models.TextField(blank=True,help_text="High level description of the slice and expected activities", max_length=1024)
    slice_url = models.URLField(blank=True, max_length=512)
    site = models.ForeignKey(Site, related_name='slices', help_text="The Site this Slice belongs to")
    max_slivers = models.IntegerField(default=10)
    service = models.ForeignKey(Service, related_name='service', null=True, blank=True)
    network = StrippedCharField(default="Private Only",null=True, blank=True, max_length=256)
    tags = generic.GenericRelation(Tag)
    serviceClass = models.ForeignKey(ServiceClass, related_name = "slices", null=True, default=get_default_serviceclass)
    creator = models.ForeignKey(User, related_name='slices', blank=True, null=True)

    # for tenant view
    default_flavor = models.ForeignKey(Flavor, related_name = "slices", null=True, blank=True)
    default_image = models.ForeignKey(Image, related_name = "slices", null=True, blank=True);
    mount_data_sets = StrippedCharField(default="GenBank",null=True, blank=True, max_length=256)

    def __unicode__(self):  return u'%s' % (self.name)

    @property
    def slicename(self):
        return "%s_%s" % (self.site.login_base, self.name)

    def save(self, *args, **kwds):
        site = Site.objects.get(id=self.site.id)
        # allow preexisting slices to keep their original name for now
        if not self.id and not self.name.startswith(site.login_base):
            raise ValidationError('slice name must begin with %s' % site.login_base)

        if self.name == site.login_base+"_":
            raise ValidationError('slice name is too short')

        if " " in self.name:
            raise ValidationError('slice name must not contain spaces')

        if self.serviceClass is None:
            # We allowed None=True for serviceClass because Django evolution
            # will fail unless it is allowed. But, we we really don't want it to
            # ever save None, so fix it up here.
            self.serviceClass = ServiceClass.get_default()
        
        # set creator on first save
        if not self.creator and hasattr(self, 'caller'):
            self.creator = self.caller

        # only admins change a slice's creator
        if 'creator' in self.changed_fields and \
            (not hasattr(self, 'caller') or not self.caller.is_admin):

            if (self._initial["creator"]==None) and (self.creator==getattr(self,"caller",None)):
                # it's okay if the creator is being set by the caller to
                # himeself on a new slice object.
                pass
            else:
                raise PermissionDenied("Insufficient privileges to change slice creator")
        
        if not self.creator:
            raise ValidationError('slice has no creator')

        super(Slice, self).save(*args, **kwds)

    def can_update(self, user):
        return user.can_update_slice(self)


    @staticmethod
    def select_by_user(user):
        if user.is_admin:
            qs = Slice.objects.all()
        else:
            # users can see slices they belong to 
            slice_ids = [sp.slice.id for sp in SlicePrivilege.objects.filter(user=user)]
            # pis can see slices at their sites
            sites = [sp.site for sp in SitePrivilege.objects.filter(user=user)\
                        if sp.role.role == 'pi']
            slice_ids.extend([s.id for s in Slice.objects.filter(site__in=sites)]) 
            qs = Slice.objects.filter(id__in=slice_ids)
        return qs

    def delete(self, *args, **kwds):
        # delete networks associated with this slice
        from core.models.network import Network
        nets = Network.objects.filter(slices=self)
        nets.delete() 
        # delete slice controllers
        slice_controllers = ControllerSlice.objects.filter(slice=self)
        slice_controllers.delete()
        # delete slice privilege
        slice_privileges = SlicePrivilege.objects.filter(slice=self)
        slice_privileges.delete() 
        # continue with normal delete
        super(Slice, self).delete(*args, **kwds) 
         

class SliceRole(PlCoreBase):
    ROLE_CHOICES = (('admin','Admin'),('default','Default'))

    role = StrippedCharField(choices=ROLE_CHOICES, unique=True, max_length=30)

    def __unicode__(self):  return u'%s' % (self.role)

class SlicePrivilege(PlCoreBase):
    user = models.ForeignKey('User', related_name='sliceprivileges')
    slice = models.ForeignKey('Slice', related_name='sliceprivileges')
    role = models.ForeignKey('SliceRole',related_name='sliceprivileges')

    composite_primary_key = ('user', 'slice', 'role')

    def __unicode__(self):  return u'%s %s %s' % (self.slice, self.user, self.role)

    def can_update(self, user):
        return user.can_update_slice(self.slice)

    @staticmethod
    def select_by_user(user):
        if user.is_admin:
            qs = SlicePrivilege.objects.all()
        else:
            sp_ids = [sp.id for sp in SlicePrivilege.objects.filter(user=user)]
            qs = SlicePrivilege.objects.filter(id__in=sp_ids)
        return qs

class ControllerSlice(PlCoreBase):
    objects = ControllerLinkManager()
    deleted_objects = ControllerLinkDeletionManager()

    controller = models.ForeignKey(Controller, related_name='controllerslices')
    slice = models.ForeignKey(Slice, related_name='controllerslices')
    tenant_id = StrippedCharField(null=True, blank=True, max_length=200, help_text="Keystone tenant id")

    composite_primary_key = ('controller', 'slice')
     
    def __unicode__(self):  return u'%s %s'  % (self.slice, self.controller)

    @staticmethod
    def select_by_user(user):
        if user.is_admin:
            qs = ControllerSlice.objects.all()
        else:
            slices = Slice.select_by_user(user)
            qs = ControllerSlice.objects.filter(slice__in=slices)
        return qs    

    def get_cpu_stats(self):
        filter = 'project_id=%s'%self.tenant_id
        return monitor.get_meter('cpu',filter,None)

    def get_bw_stats(self):
        filter = 'project_id=%s'%self.tenant_id
        return monitor.get_meter('network.outgoing.bytes',filter,None)

    def get_node_stats(self):
        return len(self.slice.slivers)
