import os
import datetime
from django.db import models
from plstackapi.core.models import PlCoreBase
from plstackapi.core.models import Site

# Create your models here.

class User(PlCoreBase):
    user_id = models.CharField(max_length=256, unique=True)
    firstname = models.CharField(help_text="person's given name", max_length=200)
    lastname = models.CharField(help_text="person's surname", max_length=200)
    email = models.EmailField(help_text="e-mail address")
    phone = models.CharField(null=True, blank=True, help_text="phone number contact", max_length=100)
    user_url = models.URLField(null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    enabled = models.BooleanField(default=True, help_text="Status for this User")
    site = models.ForeignKey(Site, related_name='users', verbose_name="Site this user will be homed too")

    def __unicode__(self):  return u'%s' % (self.email)
