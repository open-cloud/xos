from django.db import models
from core.models import User, Service, SingletonModel, PlCoreBase
import os
from django.db import models
from django.forms.models import model_to_dict

class CompositionService(SingletonModel,Service):
    class Meta:
        app_label = "servcomp"
        verbose_name = "Service Composition Service"

class Composition(PlCoreBase):
    class Meta:
        app_label = "servcomp"

    name = models.CharField(max_length=255);
    services = models.ManyToManyField(Service, through='CompositionServiceThrough', blank=True);

    def __unicode__(self):
        return self.name

class CompositionServiceThrough(PlCoreBase):
    class Meta:
        app_label = "servcomp"
        ordering = ("order", )

    composition = models.ForeignKey(Composition)
    service = models.ForeignKey(Service, related_name="compositions")
    order = models.IntegerField(default=0)

class EndUser(PlCoreBase):
    class Meta:
        app_label = "servcomp"

    email = models.CharField(max_length=255)
    firstName = models.CharField(max_length=80)
    lastName = models.CharField(max_length=80)
    macAddress = models.CharField(max_length=80)
    composition = models.ForeignKey(Composition, related_name="endUsers", blank=True, null=True)

    def __unicode__(self):
        return self.email

