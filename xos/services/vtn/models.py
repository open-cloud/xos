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
from services.cord.models import CordSubscriberRoot
import traceback
from xos.exceptions import *
from xos.config import Config

class ConfigurationError(Exception):
    pass

VTN_KIND = "VTN"

# -------------------------------------------
# VTN
# -------------------------------------------

class VTNService(Service):
    KIND = VTN_KIND

    class Meta:
        app_label = "vtn"
        verbose_name = "VTN Service"
        proxy = True

    simple_attributes = ( ("privateGatewayMac", "00:00:00:00:00:01"),
                          ("localManagementIp", "172.27.0.1/24"),
                          ("ovsdbPort", "6641"),
                          ("sshPort", "22"),
                          ("sshUser", "root"),
                          ("sshKeyFile", "/root/node_key") ,
                          ("mgmtSubnetBits", "24"),
                          ("xosEndpoint", "http://xos/"),
                          ("xosUser", "padmin@vicci.org"),
                          ("xosPassword", "letmein"),

                         )

VTNService.setup_simple_attributes()
