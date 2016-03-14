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

VTR_KIND = "vTR"

CORD_USE_VTN = getattr(Config(), "networking_use_vtn", False)

# -------------------------------------------
# VOLT
# -------------------------------------------

class VTRService(Service):
    KIND = VTR_KIND

    class Meta:
        app_label = "vtr"
        verbose_name = "vTR Service"
        proxy = True

class VTRTenant(Tenant):
    class Meta:
        proxy = True

    KIND = VTR_KIND

    TEST_CHOICES = ( ("ping", "Ping"), ("traceroute", "Trace Route"), ("tcpdump", "Tcp Dump") )
    SCOPE_CHOICES = ( ("container", "Container"), ("vm", "VM") )

    simple_attributes = ( ("test", None),
                          ("argument", None),
                          ("result", None),
                          ("result_code", None),
                          ("target_id", None),
                          ("scope", "container") )

    sync_attributes = ( 'test', 'argument', "scope" )

    def __init__(self, *args, **kwargs):
        vtr_services = VTRService.get_service_objects().all()
        if vtr_services:
            self._meta.get_field("provider_service").default = vtr_services[0].id
        super(VTRTenant, self).__init__(*args, **kwargs)

    @property
    def target(self):
        if getattr(self, "cached_target", None):
            return self.cached_target
        target_id=self.target_id
        if not target_id:
            return None
        users=CordSubscriberRoot.objects.filter(id=target_id)
        if not users:
            return None
        user=users[0]
        self.cached_target = users[0]
        return user

    @target.setter
    def target(self, value):
        if value:
            value = value.id
        if (value != self.get_attribute("target_id", None)):
            self.cached_target=None
        self.target_id = value

    def save(self, *args, **kwargs):
        super(VTRTenant, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super(VTRTenant, self).delete(*args, **kwargs)


VTRTenant.setup_simple_attributes()

