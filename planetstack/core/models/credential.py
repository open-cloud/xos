import os
from django.db import models
from core.models import PlCoreBase
from core.models import User,Site,Slice
from encrypted_fields import EncryptedCharField

class UserCredential(PlCoreBase):
    user = models.ForeignKey(User, related_name='credentials', help_text="The User this credential is associated with")

    name = models.SlugField(help_text="The credential type, e.g. ec2", max_length=128)
    key_id = models.CharField(help_text="The backend id of this credential", max_length=1024)
    enc_value = EncryptedCharField(help_text="The key value of this credential", max_length=1024)


    def __unicode__(self):
        return self.name

class SiteCredential(PlCoreBase):
    site = models.ForeignKey(Site, related_name='credentials', help_text="The User this credential is associated with")

    name = models.SlugField(help_text="The credential type, e.g. ec2", max_length=128)
    key_id = models.CharField(help_text="The backend id of this credential", max_length=1024)
    enc_value = EncryptedCharField(help_text="The key value of this credential", max_length=1024)


    def __unicode__(self):
        return self.name

class SliceCredential(PlCoreBase):
    slice = models.ForeignKey(Slice, related_name='credentials', help_text="The User this credential is associated with")

    name = models.SlugField(help_text="The credential type, e.g. ec2", max_length=128)
    key_id = models.CharField(help_text="The backend id of this credential", max_length=1024)
    enc_value = EncryptedCharField(help_text="The key value of this credential", max_length=1024)


    def __unicode__(self):
        return self.name
