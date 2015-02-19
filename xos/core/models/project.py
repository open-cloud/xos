import os
from django.db import models
from core.models import PlCoreBase

# Create your models here.

class Project(PlCoreBase):
    name = models.CharField(max_length=200, unique=True, help_text="Name of Project")

    def __unicode__(self):  return u'%s' % (self.name)

