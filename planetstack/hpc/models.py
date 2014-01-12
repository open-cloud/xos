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

    content_provider_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=254)
    enabled = models.BooleanField(default=True)
    description = models.TextField(max_length=254,null=True, blank=True,help_text="Description of Content Provider")
    serviceProvider = models.ForeignKey(ServiceProvider)

    # Note user relationships are directed not requiring a role.
    users = models.ManyToManyField(User)

    def __unicode__(self):  return u'%s' % (self.name)

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

