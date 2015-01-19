import os
from django.db import models
from core.models import PlCoreBase, Controller
from core.models.site import ControllerLinkManager, ControllerLinkDeletionManager
from django.contrib.contenttypes import generic

class DashboardView(PlCoreBase):
    name = models.CharField(max_length=200, unique=True, help_text="Name of the View")
    url = models.CharField(max_length=1024, help_text="URL of Dashboard")
    controllers = models.ManyToManyField(Controller, blank=True, related_name="dashboardviews", through='ControllerDashboardView')
    enabled = models.BooleanField(default=True)

    def __unicode__(self):  return u'%s' % (self.name)

class ControllerDashboardView(PlCoreBase):
    objects = ControllerLinkManager()
    deleted_objects = ControllerLinkDeletionManager()
    controller = models.ForeignKey(Controller, related_name='controllerdashboardviews')
    dashboardView = models.ForeignKey(DashboardView, related_name='controllerdashboardviews')
    enabled = models.BooleanField(default=True)

    url = models.CharField(max_length=1024, help_text="URL of Dashboard")



