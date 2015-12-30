from django.db import models
from core.models import User, Service, SingletonModel, PlCoreBase, DiffModelMixIn
import os
from django.db import models
from django.forms.models import model_to_dict

class UrlFilterService(SingletonModel, Service):
    class Meta:
        app_label = "urlfilter"
        verbose_name = "URL Filter Service"

