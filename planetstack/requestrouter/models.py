from core.models import User,Site,Service,SingletonModel,PlCoreBase, Slice
import os
from django.db import models
from django.forms.models import model_to_dict

# Create your models here.

class RequestRouterService(SingletonModel,Service):
    class Meta:
        app_label = "requestrouter"
        verbose_name = "Request Router Service"

    behindNat = models.BooleanField(default=False, help_text="Enables 'Behind NAT' mode.")
    defaultTTL = models.PositiveIntegerField(default=30, help_text="DNS response time-to-live(TTL)")
    defaultAction = models.CharField(max_length=30, default = "best", help_text="Review if this should be enum")
    lastResortAction = models.CharField(max_length=30, default = "random", help_text="Review if this should be enum")
    maxAnswers = models.PositiveIntegerField(default=3, help_text="Maximum number of answers in DNS response.")

    def __unicode__(self):  return u'Request Router Service'

class ServiceMap(PlCoreBase):

    class Meta:
        app_label = "requestrouter"

    name = models.SlugField(max_length=50, unique=True, blank=False, null=False, help_text="name of this service map")
    owner = models.ForeignKey(Service, help_text="service which owns this map")
    slice = models.ForeignKey(Slice, help_text="slice that implements this service")
    prefix = models.CharField(max_length=256, help_text="FQDN of the region of URI space managed by RR on behalf of this service")
	# need to fix the upload location appropriately, for now we are not using access/site map
    siteMap = models.FileField(upload_to="maps/", help_text="maps client requests to service instances", blank=True)
    accessMap = models.FileField(upload_to="maps/", help_text="specifies which client requests are allowed", blank=True)

    def siteMapName(self):
        return self.name + ".site"

    def accessMapName(self):
        return self.name + ".access"

    def __unicode__(self): return u'%s' % self.name

