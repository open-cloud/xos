from django.db import models

# Create your models here.

class PlCoreBase(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Site(PlCoreBase):
    name = models.CharField(max_length=200, unique=True, help_text="Name for this Site")
    site_url = models.URLField(help_text="Site's Home URL Page")
    enabled = models.BooleanField(default=True, help_text="Status for this Site")
    longitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    login_base = models.CharField(max_length=50, help_text="Prefix for Slices associated with this Site")
    is_public = models.BooleanField(default=True, help_text="Indicates the visibility of this site to other members")
    abbreviated_name = models.CharField(max_length=80)

    def __unicode__(self):  return u'%s' % (self.name)

class Slice(PlCoreBase):
    name = models.CharField(help_text="The Name of the Slice", max_length=80)
    SLICE_CHOICES = (('plc', 'PLC'), ('delegated', 'Delegated'), ('controller','Controller'), ('none','None'))
    instantiation = models.CharField(help_text="The instantiation type of the slice", max_length=80, choices=SLICE_CHOICES)
    omf_friendly = models.BooleanField()
    description=models.TextField(blank=True,help_text="High level description of the slice and expected activities", max_length=1024)
    slice_url = models.URLField(blank=True)
    site = models.ForeignKey(Site, related_name='slices', help_text="The Site this Node belongs too")

    def __unicode__(self):  return u'%s' % (self.name)

class DeploymentNetwork(PlCoreBase):
    name = models.CharField(max_length=200, unique=True, help_text="Name of the Deployment Network")

    def __unicode__(self):  return u'%s' % (self.name)

class SiteDeploymentNetwork(PlCoreBase):
    class Meta:
        unique_together = ['site', 'deploymentNetwork']

    site = models.ForeignKey(Site, related_name='deploymentNetworks')
    deploymentNetwork = models.ForeignKey(DeploymentNetwork, related_name='sites')
    name = models.CharField(default="Blah", max_length=100)
    

    def __unicode__(self):  return u'%s::%s' % (self.site, self.deploymentNetwork)


class Sliver(PlCoreBase):
    name = models.CharField(max_length=200, unique=True)
    slice = models.ForeignKey(Slice)
    siteDeploymentNetwork = models.ForeignKey(SiteDeploymentNetwork)

    def __unicode__(self):  return u'%s::%s' % (self.slice, self.siteDeploymentNetwork)

class Node(PlCoreBase):
    name = models.CharField(max_length=200, unique=True, help_text="Name of the Node")
    siteDeploymentNetwork = models.ForeignKey(SiteDeploymentNetwork, help_text="The Site and Deployment Network this Node belongs too.")

    def __unicode__(self):  return u'%s' % (self.name)

