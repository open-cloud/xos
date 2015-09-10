from django.db import models
from core.models import Service, PlCoreBase, Slice, Sliver, Tenant, TenantWithContainer, Node, Image, User, Flavor, Subscriber
from core.models.plcorebase import StrippedCharField
import os
from django.db import models, transaction
from django.forms.models import model_to_dict
from django.db.models import Q
from operator import itemgetter, attrgetter, methodcaller
import traceback
from xos.exceptions import *

CEILOMETER_KIND = "ceilometer"

class CeilometerService(Service):
    KIND = CEILOMETER_KIND

    class Meta:
        app_label = "ceilometer"
        verbose_name = "Ceilometer Service"
        proxy = True

class MonitoringChannel(TenantWithContainer):   # aka 'CeilometerTenant'
    class Meta:
        proxy = True

    KIND = CEILOMETER_KIND

    default_attributes = {}
    def __init__(self, *args, **kwargs):
        ceilometer_services = CeilometerService.get_service_objects().all()
        if ceilometer_services:
            self._meta.get_field("provider_service").default = ceilometer_services[0].id
        super(MonitoringChannel, self).__init__(*args, **kwargs)
        self.sliver = None

    def save(self, *args, **kwargs):
        if not self.creator:
            if not getattr(self, "caller", None):
                # caller must be set when creating a vCPE since it creates a slice
                raise XOSProgrammingError("MonitoringChannel's self.caller was not set")
            self.creator = self.caller
            if not self.creator:
                raise XOSProgrammingError("MonitoringChannel's self.creator was not set")

        super(MonitoringChannel, self).save(*args, **kwargs)
        model_policy_monitoring_channel(self.pk)

    def delete(self, *args, **kwargs):
        self.cleanup_sliver()
        super(MonitoringChannel, self).delete(*args, **kwargs)

def model_policy_monitoring_channel(pk):
    # TODO: this should be made in to a real model_policy
    with transaction.atomic():
        mc = MonitoringChannel.objects.select_for_update().filter(pk=pk)
        if not mc:
            return
        mc = mc[0]
        mc.manage_container()


