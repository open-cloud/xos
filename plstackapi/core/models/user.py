import os
import datetime
from django.db import models
from plstackapi.core.models import PlCoreBase
from plstackapi.core.models import Site
from plstackapi.openstack.driver import OpenStackDriver


# Create your models here.

class User(PlCoreBase):
    user_id = models.CharField(max_length=256, unique=True, blank=True)
    firstname = models.CharField(help_text="person's given name", max_length=200)
    lastname = models.CharField(help_text="person's surname", max_length=200)
    email = models.EmailField(help_text="e-mail address", null=True)
    password = models.CharField(max_length=256, null=True, blank=True)
    
    phone = models.CharField(null=True, blank=True, help_text="phone number contact", max_length=100)
    user_url = models.URLField(null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    enabled = models.BooleanField(default=True, help_text="Status for this User")
    site = models.ForeignKey(Site, related_name='users', verbose_name="Site this user will be homed too")

    def __unicode__(self):  return u'%s' % (self.email)

    def save(self, *args, **kwds):
        driver  = OpenStackDriver()
        if not self.user_id:
            name = self.email[:self.email.find('@')]
            user_fields = {'name': name,
                           'email': self.email,
                           'password': self.password,
                           'enabled': self.enabled}
            user = driver.create_user(**user_fields)
            self.user_id = user.id

        self.password = None
        super(User, self).save(*args, **kwds)   

    def delete(self, *args, **kwds):
        driver = OpenStackDriver()
        if self.user_id:
            driver.delete_user(self.user_id)
        super(User, self).delete(*args, **kwds)                                 
