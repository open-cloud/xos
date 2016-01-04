from core.models import Instance, PlCoreBase
from django.db import models


# Create your models here.

class Hello(PlCoreBase):
    name = models.CharField(
        max_length=254, help_text="Salutation e.g. Hello or Bonjour")
    instance_backref = models.ForeignKey(Instance, related_name="hellos")


class World(PlCoreBase):
    name = models.CharField(max_length=254, help_text="Name of planet")
    hello = models.ForeignKey(Hello)
