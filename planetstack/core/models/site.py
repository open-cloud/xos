import os
from django.db import models
from core.models import PlCoreBase
#from core.models import Deployment
from core.models import Tag
from django.contrib.contenttypes import generic
from geoposition.fields import GeopositionField

class Site(PlCoreBase):
    """
        A logical grouping of Nodes that are co-located at the same geographic location, which also typically corresponds to the Nodes' location in the physical network.
    """
    tenant_id = models.CharField(null=True, blank=True, max_length=200, help_text="Keystone tenant id")
    name = models.CharField(max_length=200, help_text="Name for this Site")
    site_url = models.URLField(null=True, blank=True, max_length=512, help_text="Site's Home URL Page")
    enabled = models.BooleanField(default=True, help_text="Status for this Site")
    location = GeopositionField()
    longitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    login_base = models.CharField(max_length=50, unique=True, help_text="Prefix for Slices associated with this Site")
    is_public = models.BooleanField(default=True, help_text="Indicates the visibility of this site to other members")
    abbreviated_name = models.CharField(max_length=80)

    deployments = models.ManyToManyField('Deployment', blank=True)
    #deployments = models.ManyToManyField('Deployment', through='SiteDeployments', blank=True)
    tags = generic.GenericRelation(Tag)

    def __unicode__(self):  return u'%s' % (self.name)

class SiteRole(PlCoreBase):

    ROLE_CHOICES = (('admin','Admin'),('pi','PI'),('tech','Tech'),('billing','Billing'))
    role = models.CharField(choices=ROLE_CHOICES, unique=True, max_length=30)

    def __unicode__(self):  return u'%s' % (self.role)

class SitePrivilege(PlCoreBase):

    user = models.ForeignKey('User', related_name='site_privileges')
    site = models.ForeignKey('Site', related_name='site_privileges')
    role = models.ForeignKey('SiteRole')

    def __unicode__(self):  return u'%s %s %s' % (self.site, self.user, self.role)

    def save(self, *args, **kwds):
        super(SitePrivilege, self).save(*args, **kwds)

    def delete(self, *args, **kwds):
        super(SitePrivilege, self).delete(*args, **kwds)

class Deployment(PlCoreBase):
    name = models.CharField(max_length=200, unique=True, help_text="Name of the Deployment")
    #sites = models.ManyToManyField('Site', through='SiteDeployments', blank=True)

    def __unicode__(self):  return u'%s' % (self.name)


class DeploymentRole(PlCoreBase):

    ROLE_CHOICES = (('admin','Admin'),)
    role = models.CharField(choices=ROLE_CHOICES, unique=True, max_length=30)

    def __unicode__(self):  return u'%s' % (self.role)

class DeploymentPrivilege(PlCoreBase):

    user = models.ForeignKey('User', related_name='deployment_privileges')
    deployment = models.ForeignKey('Deployment', related_name='deployment_privileges')
    role = models.ForeignKey('DeploymentRole')

    def __unicode__(self):  return u'%s %s %s' % (self.deployment, self.user, self.role)

class SiteDeployments(PlCoreBase):
    site = models.ForeignKey(Site)
    deployment = models.ForeignKey(Deployment)

    class Meta:
        db_table = 'site_deployments'
        #auto_created = Site

