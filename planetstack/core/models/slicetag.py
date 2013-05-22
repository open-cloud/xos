import os
from django.db import models
from core.models import PlCoreBase
from core.models import Slice

class SliceTag(PlCoreBase):
    slice = models.ForeignKey(Slice, related_name='tags')

    NAME_CHOICES = (('privatekey', 'Private Key'), ('publickey', 'Public Key'))
    name = models.CharField(help_text="The name of this tag", max_length=30, choices=NAME_CHOICES)
    value = models.CharField(help_text="The value of this tag", max_length=1024)



