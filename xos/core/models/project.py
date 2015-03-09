import os
from django.db import models
from core.models import PlCoreBase
from core.models.plcorebase import StrippedCharField

# Create your models here.

class Project(PlCoreBase):
    name = StrippedCharField(max_length=200, unique=True, help_text="Name of Project")

    def __unicode__(self):  return u'%s' % (self.name)

