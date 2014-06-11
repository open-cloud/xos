from django.db import models
from core.models import User, Service, SingletonModel, PlCoreBase
import os
from django.db import models
from django.forms.models import model_to_dict


# Create your models here.

class HpcService(SingletonModel,Service):

    class Meta:
        app_label = "hpc"
        verbose_name = "HPC Service"

class ServiceProvider(PlCoreBase):
    class Meta:
        app_label = "hpc"

    service_provider_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=254,help_text="Service Provider Name")
    description = models.TextField(max_length=254,null=True, blank=True, help_text="Description of Service Provider")
    enabled = models.BooleanField(default=True)

    def __unicode__(self):  return u'%s' % (self.name)

class ContentProvider(PlCoreBase):
    class Meta:
        app_label = "hpc"

    # legacy vicci content providers already have names.
    CP_TO_ACCOUNT = {"ON.LAB": "onlabcp",
                     "Syndicate": "syndicatecp"}

    content_provider_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=254)
    enabled = models.BooleanField(default=True)
    description = models.TextField(max_length=254,null=True, blank=True,help_text="Description of Content Provider")
    serviceProvider = models.ForeignKey(ServiceProvider)

    # Note user relationships are directed not requiring a role.
    users = models.ManyToManyField(User)

    def __unicode__(self):  return u'%s' % (self.name)

    @property
    def account(self):
        return self.CP_TO_ACCOUNT.get(self.name, self.name)

class OriginServer(PlCoreBase):
    class Meta:
        app_label = "hpc"

    origin_server_id = models.IntegerField(null=True, blank=True)
    url = models.URLField()
    contentProvider = models.ForeignKey(ContentProvider)

    authenticated = models.BooleanField(default=False, help_text="Status for this Site")
    enabled = models.BooleanField(default=True, help_text="Status for this Site")
    PROTOCOL_CHOICES = (('http', 'HTTP'),('rtmp', 'RTMP'), ('rtp', 'RTP'),('shout', 'SHOUTcast')) 
    protocol = models.CharField(default="HTTP", max_length = 12, choices=PROTOCOL_CHOICES)
    redirects = models.BooleanField(default=True, help_text="Indicates whether Origin Server redirects should be used for this Origin Server")
    description = models.TextField(null=True, blank=True, max_length=255)
    
    def __unicode__(self):  return u'%s' % (self.url)

class CDNPrefix(PlCoreBase):
    class Meta:
        app_label = "hpc"

    cdn_prefix_id = models.IntegerField(null=True, blank=True)
    prefix = models.CharField(max_length=200, help_text="Registered Prefix for Domain")
    contentProvider = models.ForeignKey(ContentProvider)
    description = models.TextField(max_length=254,null=True, blank=True,help_text="Description of Content Provider")

    defaultOriginServer = models.ForeignKey(OriginServer)
    enabled = models.BooleanField(default=True)

    def __unicode__(self):  return u'%s' % (self.prefix)

class AccessMap(models.Model):
    contentProvider = models.ForeignKey(ContentProvider)
    name = models.CharField(max_length=64, help_text="Name of the Access Map")
    description = models.TextField(null=True, blank=True,max_length=130)
    map = models.FileField(upload_to="maps/", help_text="specifies which client requests are allowed")

    def __unicode__(self):  return self.name

class SiteMap(models.Model):
    """ can be bound to a ContentProvider, ServiceProvider, or neither """
    contentProvider = models.ForeignKey(ContentProvider, blank=True, null=True)
    serviceProvider = models.ForeignKey(ServiceProvider, blank=True, null=True)
    name = models.CharField(max_length=64, help_text="Name of the Site Map")
    description = models.TextField(null=True, blank=True,max_length=130)
    map = models.FileField(upload_to="maps/", help_text="specifies how to map requests to hpc instances")

    def __unicode__(self):  return self.name
