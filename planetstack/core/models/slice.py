import os
from django.db import models
from core.models import PlCoreBase
from core.models import Site
from core.models.site import SitePrivilege
from core.models import User
from core.models import Role
from core.models import Deployment
from core.models import ServiceClass
from core.models.serviceclass import get_default_serviceclass
from core.models import Tag
from django.contrib.contenttypes import generic
from core.models import Service
from core.models import Deployment
from django.core.exceptions import ValidationError

# Create your models here.

class Slice(PlCoreBase):
    name = models.CharField(unique=True, help_text="The Name of the Slice", max_length=80)
    enabled = models.BooleanField(default=True, help_text="Status for this Slice")
    omf_friendly = models.BooleanField(default=False)
    description=models.TextField(blank=True,help_text="High level description of the slice and expected activities", max_length=1024)
    slice_url = models.URLField(blank=True, max_length=512)
    site = models.ForeignKey(Site, related_name='slices', help_text="The Site this Slice belongs to")
    max_slivers = models.IntegerField(default=10)
    imagePreference = models.CharField(default="Ubuntu 12.04 LTS", null=True, blank=True, max_length=256)
    service = models.ForeignKey(Service, related_name='service', null=True, blank=True)
    network = models.CharField(default="Private Only",null=True, blank=True, max_length=256)
    mountDataSets = models.CharField(default="GenBank",null=True, blank=True, max_length=256)
    tags = generic.GenericRelation(Tag)

    serviceClass = models.ForeignKey(ServiceClass, related_name = "slices", null=True, default=get_default_serviceclass)
    creator = models.ForeignKey(User, related_name='slices', blank=True, null=True)

    def __unicode__(self):  return u'%s' % (self.name)

    @property
    def slicename(self):
        return "%s_%s" % (self.site.login_base, self.name)

    def save(self, *args, **kwds):
        
        site = Site.objects.get(id=self.site.id)
        if not self.name.startswith(site.login_base):
            raise ValidationError('slice name must begin with %s' % site.login_base)
        
        if self.serviceClass is None:
            # We allowed None=True for serviceClass because Django evolution
            # will fail unless it is allowed. But, we we really don't want it to
            # ever save None, so fix it up here.
            self.serviceClass = ServiceClass.get_default()
        if not self.creator and hasattr(self, 'caller'):
            self.creator = self.caller
        super(Slice, self).save(*args, **kwds)

    def can_update(self, user):
        if user.is_readonly:
            return False
        if user.is_admin:
            return True
        # slice admins can update
        slice_privs = SlicePrivilege.objects.filter(user=user, slice=self)
        for slice_priv in slice_privs:
            if slice_priv.role.role == 'admin':
                return True
        # site pis can update
        site_privs = SitePrivilege.objects.filter(user=user, site=self.site)
        for site_priv in site_privs:
            if site_priv.role.role == 'pi':
                return True
 
        return False

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

class SliceRole(PlCoreBase):
    ROLE_CHOICES = (('admin','Admin'),('default','Default'))

    role = models.CharField(choices=ROLE_CHOICES, unique=True, max_length=30)

    def __unicode__(self):  return u'%s' % (self.role)

class SlicePrivilege(PlCoreBase):
    user = models.ForeignKey('User', related_name='slice_privileges')
    slice = models.ForeignKey('Slice', related_name='slice_privileges')
    role = models.ForeignKey('SliceRole')

    def __unicode__(self):  return u'%s %s %s' % (self.slice, self.user, self.role)

    def can_update(self, user):
        return self.slice.can_update(user)

    @staticmethod
    def select_by_user(user):
        if user.is_admin:
            qs = SlicePrivilege.objects.all()
        else:
            sp_ids = [sp.id for sp in SlicePrivilege.objects.filter(user=user)]
            qs = SlicePrivilege.objects.filter(id__in=sp_ids)
        return qs

class SliceDeployments(PlCoreBase):
    slice = models.ForeignKey(Slice)
    deployment = models.ForeignKey(Deployment)
    tenant_id = models.CharField(null=True, blank=True, max_length=200, help_text="Keystone tenant id")
    network_id = models.CharField(null=True, blank=True, max_length=256, help_text="Quantum network")
    router_id = models.CharField(null=True, blank=True, max_length=256, help_text="Quantum router id")
    subnet_id = models.CharField(null=True, blank=True, max_length=256, help_text="Quantum subnet id")

    def __unicode__(self):  return u'%s %s'  % (self.slice, self.deployment)

    @staticmethod
    def select_by_user(user):
        if user.is_admin:
            qs = SliceDeployments.objects.all()
        else:
            slices = Slice.select_by_user(user)
            qs = SliceDeployments.objects.filter(slice__in=slices)
        return qs    
