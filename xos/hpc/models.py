from django.db import models
from core.models import User, Service, SingletonModel, PlCoreBase
from core.models.plcorebase import StrippedCharField
import os
from django.db import models
from django.forms.models import model_to_dict
from django.db.models import Q


# Create your models here.

class HpcService(Service):

    class Meta:
        app_label = "hpc"
        verbose_name = "HPC Service"

    cmi_hostname = StrippedCharField(max_length=254, null=True, blank=True)

class ServiceProvider(PlCoreBase):
    class Meta:
        app_label = "hpc"

    hpcService = models.ForeignKey(HpcService)
    service_provider_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=254,help_text="Service Provider Name")
    description = models.TextField(max_length=254,null=True, blank=True, help_text="Description of Service Provider")
    enabled = models.BooleanField(default=True)

    def __unicode__(self):  return u'%s' % (self.name)

    @classmethod
    def select_by_hpcService(cls, hpcService):
        # This should be overridden by descendant classes that want to perform
        # filtering of visible objects by user.
        return cls.objects.filter(hpcService=hpcService)

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

    @classmethod
    def select_by_hpcService(cls, hpcService):
        # This should be overridden by descendant classes that want to perform
        # filtering of visible objects by user.
        return cls.objects.filter(serviceProvider__hpcService=hpcService)


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

    @classmethod
    def select_by_hpcService(cls, hpcService):
        # This should be overridden by descendant classes that want to perform
        # filtering of visible objects by user.
        return cls.objects.filter(contentProvider__serviceProvider__hpcService=hpcService)

class CDNPrefix(PlCoreBase):
    class Meta:
        app_label = "hpc"

    cdn_prefix_id = models.IntegerField(null=True, blank=True)
    prefix = models.CharField(max_length=200, help_text="Registered Prefix for Domain")
    contentProvider = models.ForeignKey(ContentProvider)
    description = models.TextField(max_length=254,null=True, blank=True,help_text="Description of Content Provider")

    defaultOriginServer = models.ForeignKey(OriginServer, blank=True, null=True)
    enabled = models.BooleanField(default=True)

    def __unicode__(self):  return u'%s' % (self.prefix)

    @classmethod
    def select_by_hpcService(cls, hpcService):
        # This should be overridden by descendant classes that want to perform
        # filtering of visible objects by user.
        return cls.objects.filter(contentProvider__serviceProvider__hpcService=hpcService)

class AccessMap(PlCoreBase):
    class Meta:
        app_label = "hpc"

    contentProvider = models.ForeignKey(ContentProvider)
    name = models.CharField(max_length=64, help_text="Name of the Access Map")
    description = models.TextField(null=True, blank=True,max_length=130)
    map = models.FileField(upload_to="maps/", help_text="specifies which client requests are allowed")

    def __unicode__(self):  return self.name

class SiteMap(PlCoreBase):
    class Meta:
        app_label = "hpc"

    """ can be bound to a ContentProvider, ServiceProvider, or neither """
    contentProvider = models.ForeignKey(ContentProvider, blank=True, null=True)
    serviceProvider = models.ForeignKey(ServiceProvider, blank=True, null=True)
    cdnPrefix = models.ForeignKey(CDNPrefix, blank = True, null=True)
    hpcService = models.ForeignKey(HpcService, blank = True, null=True)
    name = models.CharField(max_length=64, help_text="Name of the Site Map")
    description = models.TextField(null=True, blank=True,max_length=130)
    map = models.FileField(upload_to="maps/", help_text="specifies how to map requests to hpc instances")
    map_id = models.IntegerField(null=True, blank=True)

    def __unicode__(self):  return self.name

    def save(self, *args, **kwds):
        if (self.contentProvider) and (self.serviceProvider or self.cdnPrefix or self.hpcService):
            raise ValueError("You may only set one of contentProvider, serviceProvider, cdnPrefix, or hpcService")
        if (self.serviceProvider) and (self.cdnPrefix or self.hpcService):
            raise ValueError("You may only set one of contentProvider, serviceProvider, cdnPrefix, or hpcService")
        if (self.cdnPrefix) and (self.hpcService):
            raise ValueError("You may only set one of contentProvider, serviceProvider, cdnPrefix, or hpcService")

        super(SiteMap, self).save(*args, **kwds)

    @classmethod
    def select_by_hpcService(cls, hpcService):
        # This should be overridden by descendant classes that want to perform
        # filtering of visible objects by user.
        return cls.objects.filter(Q(hpcService=hpcService) |
                                  Q(serviceProvider__hpcService=hpcService) |
                                  Q(contentProvider__serviceProvider__hpcService=hpcService) |
                                  Q(cdnPrefix__contentProvider__serviceProvider__hpcService=hpcService))

class HpcHealthCheck(PlCoreBase):
    class Meta:
        app_label = "hpc"

    KIND_CHOICES = (('dns', 'DNS'), ('http', 'HTTP'))

    hpcService = models.ForeignKey(HpcService, blank = True, null=True)
    kind = models.CharField(max_length=30, choices=KIND_CHOICES, default="dns")
    resource_name = StrippedCharField(max_length=1024, blank=False, null=False)
    result_contains = StrippedCharField(max_length=1024, blank=True, null=True)
    result_min_size = models.IntegerField(null=True, blank=True)
    result_max_size = models.IntegerField(null=True, blank=True)

    def __unicode__(self): return self.resource_name

    @classmethod
    def select_by_hpcService(cls, hpcService):
        # This should be overridden by descendant classes that want to perform
        # filtering of visible objects by user.
        return cls.objects.filter(hpcService=hpcService)


