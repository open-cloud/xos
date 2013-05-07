import os
from django.db import models
from plstackapi.core.models import PlCoreBase
from plstackapi.core.models import Site
from plstackapi.core.models import PLUser
from plstackapi.core.models import Role
from plstackapi.core.models import DeploymentNetwork
# Create your models here.

class Slice(PlCoreBase):
    tenant_id = models.CharField(max_length=200, help_text="Keystone tenant id")
    name = models.CharField(unique=True, help_text="The Name of the Slice", max_length=80)
    enabled = models.BooleanField(default=True, help_text="Status for this Slice")
    omf_friendly = models.BooleanField()
    description=models.TextField(blank=True,help_text="High level description of the slice and expected activities", max_length=1024)
    slice_url = models.URLField(blank=True, max_length=512)
    site = models.ForeignKey(Site, related_name='slices', help_text="The Site this Node belongs too")
    network_id = models.CharField(max_length=256, help_text="Quantum network")
    router_id = models.CharField(max_length=256, help_text="Quantum router id")
    subnet_id = models.CharField(max_length=256, help_text="Quantum subnet id")

    SVC_CLASS_CHOICES = (('besteffort', 'Best Effort'), ('silver', 'Silver'), ('gold','Gold'))
    serviceClass = models.CharField(verbose_name="Service Class",default="besteffort",help_text="The Service Class of this slice", max_length=30, choices=SVC_CLASS_CHOICES)


    def __unicode__(self):  return u'%s' % (self.name)

    def save(self, *args, **kwds):
        self.os_manager.save_slice(self)
        super(Slice, self).save(*args, **kwds)

    def delete(self, *args, **kwds):
        self.os_manager.delete_slice(self)
        super(Slice, self).delete(*args, **kwds)    

class SliceMembership(PlCoreBase):
    user = models.ForeignKey('PLUser', related_name='slice_memberships')
    slice = models.ForeignKey('Slice', related_name='slice_memberships')
    role = models.ForeignKey('Role')

    def __unicode__(self):  return u'%s %s %s' % (self.slice, self.user, self.role)

    def save(self, *args, **kwds):
        self.os_manager.driver.add_user_role(self.user.user_id, self.slice.tenant_id, self.role.role_type)
        super(SliceMembership, self).save(*args, **kwds)

    def delete(self, *args, **kwds):
        self.os_manager.driver.delete_user_role(self.user.user_id, self.slice.tenant_id, self.role.role_type)
        super(SliceMembership, self).delete(*args, **kwds)
