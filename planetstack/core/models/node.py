import os
from django.db import models
from core.models import PlCoreBase
from core.models import SiteDeployments, Controller
from core.models import Tag
from django.contrib.contenttypes import generic

# Create your models here.

class Node(PlCoreBase):
    name = models.CharField(max_length=200, unique=True, help_text="Name of the Node")
    site_deployment = models.ForeignKey(SiteDeployments, related_name='nodes')
    tags = generic.GenericRelation(Tag)

    def __unicode__(self):  return u'%s' % (self.name)

