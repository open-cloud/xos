from core.models import PlCoreBase,SingletonModel
from django.db import models

class PlanetStackService(PlCoreBase):
    description = models.TextField(max_length=254,null=True, blank=True,help_text="Description of Service")
    enabled = models.BooleanField(default=True)
    serviceName = models.CharField(max_length=30, help_text="Service Name")

    def __unicode__(self): return u'%s' % (self.serviceName)
