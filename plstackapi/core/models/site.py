import os
from django.db import models
from plstackapi.core.models import PlCoreBase
from plstackapi.core.models import DeploymentNetwork


class Site(PlCoreBase):

    tenant_id = models.CharField(max_length=200, help_text="Keystone tenant id")
    name = models.CharField(max_length=200, help_text="Name for this Site")
    site_url = models.URLField(null=True, blank=True, max_length=512, help_text="Site's Home URL Page")
    enabled = models.BooleanField(default=True, help_text="Status for this Site")
    longitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    login_base = models.CharField(max_length=50, unique=True, help_text="Prefix for Slices associated with this Site")
    is_public = models.BooleanField(default=True, help_text="Indicates the visibility of this site to other members")
    abbreviated_name = models.CharField(max_length=80)

    deployments = models.ManyToManyField(DeploymentNetwork, blank=True, related_name='sites')

    def __unicode__(self):  return u'%s' % (self.name)

    def save(self, *args, **kwds):
        if not self.tenant_id:
            tenant = self.driver.create_tenant(tenant_name=self.login_base, 
                                               description=self.name, 
                                               enabled=self.enabled)
            self.tenant_id = tenant.id
        # update the record
        if self.id:
            self.driver.update_tenant(self.tenant_id, 
                                      name=self.login_base,
                                      description=self.name,
                                      enabled=self.enabled)

        super(Site, self).save(*args, **kwds)               


    def delete(self, *args, **kwds):
        if self.tenant_id:
            self.driver.delete_tenant(self.tenant_id)
        super(Site, self).delete(*args, **kwds)         
        

class SitePrivilege(PlCoreBase):

    user = models.ForeignKey('PLUser', related_name='site_privileges')
    site = models.ForeignKey('Site', related_name='site_privileges')
    role = models.ForeignKey('Role')

    def __unicode__(self):  return u'%s %s %s' % (self.site, self.user, self.role)

    def save(self, *args, **kwds):
        self.driver.add_user_role(self.user.user_id, self.site.tenant_id, self.role.role_type)
        super(SitePrivilege, self).save(*args, **kwds)

    def delete(self, *args, **kwds):
        self.driver.delete_user_role(self.user.user_id, self.site.tenant_id, self.role.role_type)
        super(SitePrivilege, self).delete(*args, **kwds)


