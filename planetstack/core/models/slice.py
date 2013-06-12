import os
from django.db import models
from core.models import PlCoreBase
from core.models import Site
from core.models import User
from core.models import Role
from core.models import Deployment
from core.models import ServiceClass

# Create your models here.

class Slice(PlCoreBase):
    tenant_id = models.CharField(max_length=200, help_text="Keystone tenant id")
    name = models.CharField(unique=True, help_text="The Name of the Slice", max_length=80)
    enabled = models.BooleanField(default=True, help_text="Status for this Slice")
    omf_friendly = models.BooleanField()
    description=models.TextField(blank=True,help_text="High level description of the slice and expected activities", max_length=1024)
    slice_url = models.URLField(blank=True, max_length=512)
    site = models.ForeignKey(Site, related_name='slices', help_text="The Site this Node belongs too")
    network_id = models.CharField(null=True, blank=True, max_length=256, help_text="Quantum network")
    router_id = models.CharField(null=True, blank=True, max_length=256, help_text="Quantum router id")
    subnet_id = models.CharField(null=True, blank=True, max_length=256, help_text="Quantum subnet id")

    serviceClass = models.ForeignKey(ServiceClass, related_name = "slices", null=True, default=ServiceClass.get_default)
    creator = models.ForeignKey(User, related_name='slices', blank=True, null=True)

    def __unicode__(self):  return u'%s' % (self.name)

    def save(self, *args, **kwds):
        if self.serviceClass is None:
            # We allowed None=True for serviceClass because Django evolution
            # will fail unless it is allowed. But, we we really don't want it to
            # ever save None, so fix it up here.
            self.serviceClass = ServiceClass.get_default()
        if not self.creator and hasattr(self, 'caller'):
            self.creator = self.caller
        super(Slice, self).save(*args, **kwds)

class SliceMembership(PlCoreBase):
    user = models.ForeignKey('User', related_name='slice_memberships')
    slice = models.ForeignKey('Slice', related_name='slice_memberships')
    role = models.ForeignKey('Role')

    def __unicode__(self):  return u'%s %s %s' % (self.slice, self.user, self.role)

    def save(self, *args, **kwds):
        if not hasattr(self, 'os_manager'):
            from openstack.manager import OpenStackManager
            setattr(self, 'os_manager', OpenStackManager())
            if self.os_manager.driver:
                self.os_manager.driver.add_user_role(self.user.kuser_id, self.slice.tenant_id, self.role.role_type)
        super(SliceMembership, self).save(*args, **kwds)

    def delete(self, *args, **kwds):
        if not hasattr(self, 'os_manager'):
            from openstack.manager import OpenStackManager
            setattr(self, 'os_manager', OpenStackManager())
            if self.os_manager.driver:
                self.os_manager.driver.delete_user_role(self.user.kuser_id, self.slice.tenant_id, self.role.role_type)
        super(SliceMembership, self).delete(*args, **kwds)
