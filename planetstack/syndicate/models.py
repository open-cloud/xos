from core.models import User,Site,Service,SingletonModel,PlCoreBase
import os
from django.db import models
from django.forms.models import model_to_dict
from bitfield import BitField

# Create your models here.

class SyndicateService(SingletonModel,Service):
    class Meta:
        app_label = "syndicate"
        verbose_name = "Syndicate Service"
        verbose_name_plural = "Syndicate Service"

    def __unicode__(self):  return u'Syndicate Service'

class SyndicateUser(models.Model):

    user = models.ForeignKey(User)
    is_admin = models.BooleanField(default=False, help_text="Indicates this user has Administrative purposes for the Syndicate Service")
    max_volumes = models.PositiveIntegerField(help_text="Maximum number of Volumes this user may create.", default=1)
    max_UGs = models.PositiveIntegerField(help_text="Maximum number of User Gateways this user may create.", default=500)
    max_RGs = models.PositiveIntegerField(help_text="Maximum number of Replica Gateways this user may create.", default=500)
    max_AGs = models.PositiveIntegerField(help_text="Maximum number of Aquisition Gateways this user may create.", default=10)
    
    def __unicode__(self):  return self.user.email
    
class Volume(models.Model):
    name = models.CharField(max_length=64, help_text="Human-readable, searchable name of the Volume")
    owner_id = models.ForeignKey(SyndicateUser, verbose_name='Owner')
    description = models.TextField(null=True, blank=True,max_length=130, help_text="Human-readable description of what this Volume is used for.")
    blocksize = models.PositiveIntegerField(help_text="Number of bytes per block.")
    private = models.BooleanField(default=True, help_text="Indicates if the Volume is visible to users other than the Volume Owner and Syndicate Administrators.")
    archive = models.BooleanField(default=True, help_text="Indicates if this Volume is read-only, and only an Aquisition Gateway owned by the Volume owner (or Syndicate admin) can write to it.")
    metadata_public_key = models.TextField(null=True, blank=True, max_length=1024, help_text="Public key Gateways will use to verify the authenticity of metadata from this Volume")
    metadata_private_key = models.TextField(null=True, blank=True, max_length=1024, help_text="Private key the Volume should use to sign metadata served to Gateways")
    api_public_key = models.TextField(null=True, blank=True, max_length=1024, help_text="Public key used to verify writes to these fields from Volume owner")

    file_quota = models.IntegerField(help_text='Maximum number of files and directories allowed in this Volume (-1 means "unlimited")')

    default_gateway_caps = BitField(flags=('GATEWAY_CAP_READ_DATA','GATEWAY_CAP_READ_METADATA', 'GATEWAY_CAP_WRITE_DATA', 'GATEWAY_CAP_WRITE_METADATA', 'GATEWAY_CAP_COORDINATE'), verbose_name='Default Gateway Capabilities')
    #default_gateway_caps = models.PositiveIntegerField(verbose_name='Default Gateway Capabilities')
    #default_gateway_caps2 = models.CharField(max_length=32,null=True,default = "readonly", verbose_name='Default Gateway Capabilities')

    def __unicode__(self):  return self.name

class VolumeAccessRight(models.Model):
    owner_id = models.ForeignKey(SyndicateUser, verbose_name='user')
    volume = models.ForeignKey(Volume)
    gateway_caps = BitField(flags=('GATEWAY_CAP_READ_DATA','GATEWAY_CAP_READ_METADATA', 'GATEWAY_CAP_WRITE_DATA', 'GATEWAY_CAP_WRITE_METADATA', 'GATEWAY_CAP_COORDINATE'), verbose_name='Gateway Capabilities')
    #gateway_caps = models.PositiveIntegerField(verbose_name='Gateway Capabilities')
    #gateway_caps2 = models.CharField(max_length=32, default='readonly',null=True,verbose_name='Default Gateway Capabilities')

    def __unicode__(self):  return self.owner_id.user.email

class VolumeAccessRequest(models.Model):
    owner_id = models.ForeignKey(SyndicateUser, verbose_name='user')
    volume = models.ForeignKey(Volume)
    message = models.TextField(null=True, blank=True, max_length=1024, help_text="Description of why the user wants access to the volume.")
    gateway_caps = BitField(flags=('GATEWAY_CAP_READ_DATA','GATEWAY_CAP_READ_METADATA', 'GATEWAY_CAP_WRITE_DATA', 'GATEWAY_CAP_WRITE_METADATA', 'GATEWAY_CAP_COORDINATE'), verbose_name='Gateway Capabilities')
    #gateway_caps = models.PositiveIntegerField(verbose_name='Gateway Capabilities')
    #gateway_caps2 = models.CharField(max_length=32,default='readonly',null=True,verbose_name='Default Gateway Capabilities')

    def __unicode__(self):  return self.owner_id.user.email
