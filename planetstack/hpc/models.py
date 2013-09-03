from django.db import models
from core.models import User
import os
from django.db import models
from django.forms.models import model_to_dict


# Create your models here.

class HpcCoreBase(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        app_label = "hpc"

    def __init__(self, *args, **kwargs):
        super(HpcCoreBase, self).__init__(*args, **kwargs)
        self.__initial = self._dict

    @property
    def diff(self):
        d1 = self.__initial
        d2 = self._dict
        diffs = [(k, (v, d2[k])) for k, v in d1.items() if v != d2[k]]
        return dict(diffs)

    @property
    def has_changed(self):
        return bool(self.diff)

    @property
    def changed_fields(self):
        return self.diff.keys()

    def get_field_diff(self, field_name):
        return self.diff.get(field_name, None)

    def save(self, *args, **kwargs):
        super(HpcCoreBase, self).save(*args, **kwargs)

        self.__initial = self._dict

    @property
    def _dict(self):
        return model_to_dict(self, fields=[field.name for field in
                             self._meta.fields])

    
class ServiceProvider(HpcCoreBase):
    name = models.CharField(max_length=254,help_text="Service Provider Name")
    description = models.TextField(max_length=254,null=True, blank=True, help_text="Description of Service Provider")
    enabled = models.BooleanField(default=True)

    def __unicode__(self):  return u'%s' % (self.name)

class ContentProvider(HpcCoreBase):
    name = models.CharField(max_length=254)
    enabled = models.BooleanField(default=True)
    description = models.TextField(max_length=254,null=True, blank=True,help_text="Description of Content Provider")
    serviceProvider = models.ForeignKey(ServiceProvider)

    # Note user relationships are directed not requiring a role.
    users = models.ManyToManyField(User)

    def __unicode__(self):  return u'%s' % (self.name)

class OriginServer(HpcCoreBase):
    url = models.URLField()
    contentProvider = models.ForeignKey(ContentProvider)

    authenticated = models.BooleanField(default=False, help_text="Status for this Site")
    enabled = models.BooleanField(default=True, help_text="Status for this Site")
    PROTOCOL_CHOICES = (('http', 'HTTP'),('rtmp', 'RTMP'), ('rtp', 'RTP'),('shout', 'SHOUTcast')) 
    protocol = models.CharField(default="HTTP", max_length = 12, choices=PROTOCOL_CHOICES)
    redirects = models.BooleanField(default=True, help_text="Indicates whether Origin Server redirects should be used for this Origin Server")
    description = models.TextField(null=True, blank=True, max_length=255)
    
    def __unicode__(self):  return u'%s' % (self.url)

class CDNPrefix(HpcCoreBase):
    prefix = models.CharField(max_length=200, help_text="Registered Prefix for Domain")
    contentProvider = models.ForeignKey(ContentProvider)
    description = models.TextField(max_length=254,null=True, blank=True,help_text="Description of Content Provider")

    defaultOriginServer = models.ForeignKey(OriginServer)
    enabled = models.BooleanField(default=True)

    def __unicode__(self):  return u'%s' % (self.prefix)

