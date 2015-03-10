import os
from django.db import models
from core.models import PlCoreBase
from core.models import User,Site,Slice,Controller
from core.models.plcorebase import StrippedCharField
from encrypted_fields import EncryptedCharField
from core.models import Controller,ControllerLinkManager,ControllerLinkDeletionManager

class UserCredential(PlCoreBase):
    user = models.ForeignKey(User, related_name='usercredentials', help_text="The User this credential is associated with")

    name = models.SlugField(help_text="The credential type, e.g. ec2", max_length=128)
    key_id = StrippedCharField(help_text="The backend id of this credential", max_length=1024)
    enc_value = EncryptedCharField(help_text="The key value of this credential", max_length=1024)


    def __unicode__(self):
        return self.name

class SiteCredential(PlCoreBase):
    site = models.ForeignKey(Site, related_name='sitecredentials', help_text="The User this credential is associated with")

    name = models.SlugField(help_text="The credential type, e.g. ec2", max_length=128)
    key_id = StrippedCharField(help_text="The backend id of this credential", max_length=1024)
    enc_value = EncryptedCharField(help_text="The key value of this credential", max_length=1024)


    def __unicode__(self):
        return self.name

class SliceCredential(PlCoreBase):
    slice = models.ForeignKey(Slice, related_name='slicecredentials', help_text="The User this credential is associated with")

    name = models.SlugField(help_text="The credential type, e.g. ec2", max_length=128)
    key_id = StrippedCharField(help_text="The backend id of this credential", max_length=1024)
    enc_value = EncryptedCharField(help_text="The key value of this credential", max_length=1024)


    def __unicode__(self):
        return self.name

class ControllerCredential(PlCoreBase):
    objects = ControllerLinkManager()
    deleted_objects = ControllerLinkDeletionManager()
    controller = models.ForeignKey(Controller, related_name='controllercredentials', help_text="The User this credential is associated with")

    name = models.SlugField(help_text="The credential type, e.g. ec2", max_length=128)
    key_id = models.CharField(help_text="The backend id of this credential", max_length=1024)
    enc_value = EncryptedCharField(help_text="The key value of this credential", max_length=1024)


    def __unicode__(self):
        return self.name
