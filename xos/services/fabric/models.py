from django.db import models
from core.models import Service, PlCoreBase, Slice, Instance, Tenant, TenantWithContainer, Node, Image, User, Flavor, Subscriber, NetworkParameter, NetworkParameterType, Port, AddressPool
from core.models.plcorebase import StrippedCharField
import os
from django.db import models, transaction
from django.forms.models import model_to_dict
from django.db.models import Q
from operator import itemgetter, attrgetter, methodcaller
from core.models import Tag
from core.models.service import LeastLoadedNodeScheduler
import traceback
from xos.exceptions import *
from xos.config import Config

class ConfigurationError(Exception):
    pass

FABRIC_KIND = "fabric"

CORD_USE_VTN = getattr(Config(), "networking_use_vtn", False)

class FabricService(Service):
    KIND = FABRIC_KIND

    class Meta:
        app_label = "fabric"
        verbose_name = "Fabric Service"
        proxy = True

    simple_attributes = ( ("autoconfig", True) )

FabricService.setup_simple_attributes()
