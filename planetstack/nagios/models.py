from core.models import User,Site,Service,SingletonModel,PlCoreBase, Slice
import os
from django.db import models
from django.forms.models import model_to_dict

# Create your models here.

class NagiosService(SingletonModel,Service):
    class Meta:
        app_label = "nagios"
        verbose_name = "Nagios Service"

    def __unicode__(self):  return u'Nagios Service'

