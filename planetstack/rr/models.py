from django.db import models
from core.models import User, Service, SingletonModel, PlCoreBase
import os
from django.db import models
from django.forms.models import model_to_dict


# Create your models here.

class RRService(SingletonModel,Service):

    class Meta:
        app_label = "rr"
        verbose_name = "RR Service"

class DNSName(PlCoreBase):
    class Meta:
        app_label = "rr"

    cdn_prefix_id = models.IntegerField(null=True, blank=True)
    prefix = models.CharField(max_length=200, help_text="DNS Name")
    contentProvider = models.ForeignKey(ContentProvider)
    description = models.TextField(max_length=254,null=True, blank=True,help_text="Description of DNS Name")

    defaultOriginServer = models.ForeignKey(OriginServer, blank=True, null=True)
    enabled = models.BooleanField(default=True)

    def __unicode__(self):  return u'%s' % (self.prefix)


