import os
from django.db import models
from core.models import PlCoreBase
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

# Create your models here.

class Tag(PlCoreBase):

    name = models.SlugField(help_text="The name of this tag", max_length=128)
    value = models.CharField(help_text="The value of this tag", max_length=1024)

    # The required fields to do a ObjectType lookup, and object_id assignment
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return self.name

