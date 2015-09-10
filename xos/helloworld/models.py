from django.db import models
from core.models import User, Service, SingletonModel, PlCoreBase, Sliver
from core.models.plcorebase import StrippedCharField
import os
from django.db import models
from django.forms.models import model_to_dict
from django.db.models import Q


# Create your models here.

class Hello(PlCoreBase):
    name = models.CharField(max_length=254,help_text="Salutation e.g. Hello or Bonjour")
    sliver_backref = models.ForeignKey(Sliver)
    
class World(PlCoreBase):
    name = models.CharField(max_length=254,help_text="Name of planet")
    hello = models.ForeignKey(Hello) 
