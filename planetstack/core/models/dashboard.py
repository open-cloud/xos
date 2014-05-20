import os
from django.db import models
from core.models import PlCoreBase
from django.contrib.contenttypes import generic

class DashboardView(PlCoreBase):
    name = models.CharField(max_length=200, unique=True, help_text="Name of the View")
    url = models.CharField(max_length=1024, help_text="URL of Dashboard")

    def __unicode__(self):  return u'%s' % (self.name)

