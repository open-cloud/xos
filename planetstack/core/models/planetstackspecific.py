import os
from django.db import models
from core.models import PlCoreBase

# Create your models here.

class PlanetStack(PlCoreBase):
    description = models.CharField(max_length=200, unique=True, default="PlanetStack", help_text="Used for scoping of roles at the PlanetStack Application level")

    class Meta:
        verbose_name_plural = "PlanetStack"
        app_label = "core"

    def __unicode__(self):  return u'%s' % (self.description)

class PlanetStackRole(PlCoreBase):
    ROLE_CHOICES = (('admin','Admin'),)
    role = models.CharField(choices=ROLE_CHOICES, unique=True, max_length=30)

    def __unicode__(self):  return u'%s' % (self.role)

class PlanetStackPrivilege(PlCoreBase):
    user = models.ForeignKey('User', related_name='planetstackprivileges')
    planetstack = models.ForeignKey('PlanetStack', related_name='planetstackprivileges', default=1)
    role = models.ForeignKey('PlanetStackRole')

    def __unicode__(self):  return u'%s %s %s' % (self.planetstack, self.user, self.role)



