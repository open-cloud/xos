from core.models import User,Site,Service,SingletonModel,PlCoreBase
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
    
    def __unicode__(self):  return u'RequestRouterService'

class ClientMap(models.Model):
    site = models.OneToOneField(Site, unique=True)
    name = models.CharField(max_length=64, help_text="Name of the Client Map")
    description = models.TextField(null=True, blank=True,max_length=130)
    
