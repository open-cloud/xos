import os
from django.db import models
from core.models import PlCoreBase
from core.models import Slice
from core.models.plcorebase import StrippedCharField

class SliceTag(PlCoreBase):
    slice = models.ForeignKey(Slice, related_name='slicetags')

    NAME_CHOICES = (('privatekey', 'Private Key'), ('publickey', 'Public Key'))
    name = StrippedCharField(help_text="The name of this tag", max_length=30, choices=NAME_CHOICES)
    value = StrippedCharField(help_text="The value of this tag", max_length=1024)

    def can_update(self, user):
        return user.can_update_slice(self.slice)

    @staticmethod
    def select_by_user(user):
        if user.is_admin:
            qs = SliceTag.objects.all()
        else:
            slices = Slice.select_by_user(user)
            qs = SliceTag.objects.filter(slice__in=slices)
        return qs
