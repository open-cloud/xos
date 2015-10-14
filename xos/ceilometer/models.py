from django.db import models
from core.models import Service, PlCoreBase, Slice, Instance, Tenant, TenantWithContainer, Node, Image, User, Flavor, Subscriber
from core.models.plcorebase import StrippedCharField
import os
from django.db import models, transaction
from django.forms.models import model_to_dict
from django.db.models import Q
from operator import itemgetter, attrgetter, methodcaller
import traceback
from xos.exceptions import *
from core.models import SlicePrivilege, SitePrivilege
from sets import Set

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

    sync_attributes = ("private_ip", "private_mac",
                       "ceilometer_ip", "ceilometer_mac",
                       "nat_ip", "nat_mac",)

    default_attributes = {}
    def __init__(self, *args, **kwargs):
        ceilometer_services = CeilometerService.get_service_objects().all()
        if ceilometer_services:
            self._meta.get_field("provider_service").default = ceilometer_services[0].id
        super(MonitoringChannel, self).__init__(*args, **kwargs)

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
        self.cleanup_container()
        super(MonitoringChannel, self).delete(*args, **kwargs)

    @property
    def addresses(self):
        if not self.instance:
            return {}

        addresses = {}
        for ns in self.instance.ports.all():
            if "private" in ns.network.name.lower():
                addresses["private"] = (ns.ip, ns.mac)
            elif "nat" in ns.network.name.lower():
                addresses["nat"] = (ns.ip, ns.mac)
            elif "ceilometer_client_access" in ns.network.labels.lower():
                addresses["ceilometer"] = (ns.ip, ns.mac)
        return addresses

    @property
    def nat_ip(self):
        return self.addresses.get("nat", (None, None))[0]

    @property
    def nat_mac(self):
        return self.addresses.get("nat", (None, None))[1]

    @property
    def private_ip(self):
        return self.addresses.get("nat", (None, None))[0]

    @property
    def private_mac(self):
        return self.addresses.get("nat", (None, None))[1]

    @property
    def ceilometer_ip(self):
        return self.addresses.get("ceilometer", (None, None))[0]

    @property
    def ceilometer_mac(self):
        return self.addresses.get("ceilometer", (None, None))[1]

    @property
    def site_tenant_list(self):
        tenant_ids = Set()
        for sp in SitePrivilege.objects.filter(user=self.creator):
            site = sp.site
            for cs in site.controllersite.all():
               if cs.tenant_id:
                   tenant_ids.add(cs.tenant_id)
        return tenant_ids

    @property
    def slice_tenant_list(self):
        tenant_ids = Set()
        for sp in SlicePrivilege.objects.filter(user=self.creator):
            slice = sp.slice
            for cs in slice.controllerslices.all():
               if cs.tenant_id:
                   tenant_ids.add(cs.tenant_id)
        for slice in Slice.objects.filter(creator=self.creator):
            for cs in slice.controllerslices.all():
                if cs.tenant_id:
                    tenant_ids.add(cs.tenant_id)
        return tenant_ids

    @property
    def tenant_list(self):
        return self.slice_tenant_list | self.site_tenant_list

    @property
    def tenant_list_str(self):
        return ", ".join(self.tenant_list)

    @property
    def ceilometer_url(self):
        if not self.ceilometer_ip:
            return None
        return "http://" + self.private_ip + ":8888/"

def model_policy_monitoring_channel(pk):
    # TODO: this should be made in to a real model_policy
    with transaction.atomic():
        mc = MonitoringChannel.objects.select_for_update().filter(pk=pk)
        if not mc:
            return
        mc = mc[0]
        mc.manage_container()


