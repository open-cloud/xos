from core.models import User,Site,Service,SingletonModel,PlCoreBase, Slice
import os
from django.db import models
from django.forms.models import model_to_dict

# Create your models here.

class CassandraService(SingletonModel,Service):
    class Meta:
        app_label = "cassandra"
        verbose_name = "Cassandra Service"

    clusterSize = models.PositiveIntegerField(default=1)
    replicationFactor = models.PositiveIntegerField(default=1)

    def __unicode__(self):  return u'Cassandra Service'

