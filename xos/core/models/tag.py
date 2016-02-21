import os
from django.db import models
from core.models import PlCoreBase
from core.models import Service
from core.models.plcorebase import StrippedCharField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

# Create your models here.

class Tag(PlCoreBase):

    service = models.ForeignKey(Service, related_name='tags', help_text="The Service this Tag is associated with")

    name = models.SlugField(help_text="The name of this tag", max_length=128)
    value = StrippedCharField(help_text="The value of this tag", max_length=1024)

    # The required fields to do a ObjectType lookup, and object_id assignment
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return self.name


    def can_update(self, user):
        return user.can_update_root()

    @classmethod
    def select_by_content_object(cls, obj):
        return cls.objects.filter(content_type=ContentType.objects.get_for_model(obj), object_id=obj.id)

    @staticmethod
    def select_by_user(user):
        return Tag.objects.all()
