import os
from django.db import models
from plstackapi.core.models import PlCoreBase
from plstackapi.core.models import User
from plstackapi.openstack.driver import OpenStackDriver

# Create your models here.

class Key(PlCoreBase):
    name = models.CharField(max_length=256, unique=True)
    key_id = models.CharField(max_length=256, unique=True)
    key = models.CharField(max_length=512)
    type = models.CharField(max_length=256)
    blacklisted = models.BooleanField(default=False)
    user = models.ForeignKey(User, related_name='keys')

    def __unicode__(self):  return u'%s' % (self.name)

    def save(self, *args, **kwds):
        driver = OpenStackDriver()
        if not self.key_id:
            key_fields = {'name': self.name,
                          'key': self.key}
            nova_key = driver.create_keypair(**key_fields)
            print nova_key.id
            self.key_id = nova_key.id
        super(Key, self).save(*args, **kwds)

    def delete(self, *args, **kwds):
        driver  = OpenStackDriver()
        if self.key_id:
            driver.delete_keypair(self.key_id)
        super(Key, self).delete(*args, **kwds) 
    
