import os
from django.db import models
from core.models import PlCoreBase
from core.models import Service
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

# Create your models here.

class Tag(PlCoreBase):

    service = models.ForeignKey(Service, related_name='tags', help_text="The Service this Tag is associated with")

    name = models.SlugField(help_text="The name of this tag", max_length=128)
    value = models.CharField(help_text="The value of this tag", max_length=1024)

    # The required fields to do a ObjectType lookup, and object_id assignment
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return self.name


    def can_update(self, user):
        if user.is_admin:
            return True
        return False

    def save_by_user(self, user, *args, **kwds):
        if self.can_update(user):
            super(Tag, self).save(*args, **kwds)

    @staticmethod
    def select_by_user(user):
        return Tag.objects.all()
