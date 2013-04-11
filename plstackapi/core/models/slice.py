import os
from django.db import models
from plstackapi.core.models import PlCoreBase
from plstackapi.core.models import Site
from plstackapi.core.models import User
from plstackapi.core.models import Role
from plstackapi.core.models import DeploymentNetwork

from plstackapi.openstack.driver import OpenStackDriver

# Create your models here.

class Slice(PlCoreBase):
    tenant_id = models.CharField(max_length=200, help_text="Keystone tenant id")
    name = models.CharField(help_text="The Name of the Slice", max_length=80)
    enabled = models.BooleanField(default=True, help_text="Status for this Slice")
    SLICE_CHOICES = (('plc', 'PLC'), ('delegated', 'Delegated'), ('controller','Controller'), ('none','None'))
    instantiation = models.CharField(help_text="The instantiation type of the slice", max_length=80, choices=SLICE_CHOICES)
    omf_friendly = models.BooleanField()
    description=models.TextField(blank=True,help_text="High level description of the slice and expected activities", max_length=1024)
    slice_url = models.URLField(blank=True, max_length=512)
    site = models.ForeignKey(Site, related_name='slices', help_text="The Site this Node belongs too")
    network_id = models.CharField(max_length=256, help_text="Quantum network")
    router_id = models.CharField(max_length=256, help_text="Quantum router id")

    def __unicode__(self):  return u'%s' % (self.name)

    def save(self, *args, **kwds):
        # sync keystone tenant
        driver  = OpenStackDriver()

        if not self.id:
            tenant = driver.create_tenant(tenant_name=self.name,
                                          description=self.description,
                                          enabled=self.enabled)
            self.tenant_id = tenant.id
            
            # create a network  
            network = driver.create_network(name=self.name)
            self.network_id = network['id']        
            # create router
            router = driver.create_router(name=self.name)
            self.router_id = router['id']     

/bin/sh: 1: command not found
            # update record
            self.driver.update_tenant(self.tenant_id, name=self.name,
                                      description=self.description, enabled=self.enabled)
        super(Slice, self).save(*args, **kwds)

    def delete(self, *args, **kwds):
        # delete keystone tenant
        driver  = OpenStackDriver()
        driver.delete_tenant(self.tenant_id)
        super(Slice, self).delete(*args, **kwds)

class SliceMembership(PlCoreBase):
    user = models.ForeignKey('User', related_name='slice_memberships')
    slice = models.ForeignKey('Slice', related_name='slice_memberships')
    role = models.ForeignKey('Role')

    def __unicode__(self):  return u'%s %s %s' % (self.slice, self.user, self.role)

    def save(self, *args, **kwds):
        driver  = OpenStackDriver()
        driver.add_user_role(user_id=user.user_id,
                             tenant_id=slice.tenant_id,
                             role_name=role.name)
        super(SliceMembership, self).save(*args, **kwds)

    def delete(self, *args, **kwds):
        driver = OpenStackDriver()
        driver.delete_user_role(user_id=user.user_id,
                                tenant_id=slice.tenant_id,
                                role_name=role.name)
        super(SliceMembership, self).delete(*args, **kwds)
