from django.db import models
from core.models import Service
import traceback
from xos.exceptions import *
from xos.config import Config

FABRIC_KIND = "fabric"

class FabricService(Service):
    KIND = FABRIC_KIND

    class Meta:
        app_label = "fabric"
        verbose_name = "Fabric Service"

    autoconfig = models.BooleanField(default=True, help_text="Autoconfigure the fabric")
