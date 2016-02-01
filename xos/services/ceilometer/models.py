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
from urlparse import urlparse

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
                       "nat_ip", "nat_mac", "ceilometer_port",)

    default_attributes = {}
    def __init__(self, *args, **kwargs):
        ceilometer_services = CeilometerService.get_service_objects().all()
        if ceilometer_services:
            self._meta.get_field("provider_service").default = ceilometer_services[0].id
        super(MonitoringChannel, self).__init__(*args, **kwargs)
        self.set_attribute("use_same_instance_for_multiple_tenants", True)

    def can_update(self, user):
        #Allow creation of this model instances for non-admin users also
        return True

    def save(self, *args, **kwargs):
        if not self.creator:
            if not getattr(self, "caller", None):
                # caller must be set when creating a monitoring channel since it creates a slice
                raise XOSProgrammingError("MonitoringChannel's self.caller was not set")
            self.creator = self.caller
            if not self.creator:
                raise XOSProgrammingError("MonitoringChannel's self.creator was not set")

        if self.pk is None:
            #Allow only one monitoring channel per user
            channel_count = sum ( [1 for channel in MonitoringChannel.objects.filter(kind=CEILOMETER_KIND) if (channel.creator == self.creator)] )
            if channel_count > 0:
                raise XOSValidationError("Already %s channels exist for user Can only create max 1 MonitoringChannel instance per user" % str(channel_count))

        super(MonitoringChannel, self).save(*args, **kwargs)
        model_policy_monitoring_channel(self.pk)

    def delete(self, *args, **kwargs):
        self.cleanup_container()
        super(MonitoringChannel, self).delete(*args, **kwargs)

    @property
    def addresses(self):
        if (not self.id) or (not self.instance):
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
        if self.creator.is_admin:
            #TODO: Ceilometer publishes the SDN meters without associating to any tenant IDs.
            #For now, ceilometer code is changed to pusblish all such meters with tenant
            #id as "default_admin_tenant". Here add that default tenant as authroized tenant_id
            #for all admin users. 
            tenant_ids.add("default_admin_tenant")
        return tenant_ids

    @property
    def tenant_list(self):
        return self.slice_tenant_list | self.site_tenant_list

    @property
    def tenant_list_str(self):
        return ", ".join(self.tenant_list)

    @property
    def ceilometer_port(self):
        # TODO: Find a better logic to choose unique ceilometer port number for each instance 
        if not self.id:
            return None
        return 8888+self.id

    @property
    def ceilometer_url(self):
        if not self.ceilometer_ip:
            return None
        return "http://" + self.private_ip + ":" + str(self.ceilometer_port) + "/"

def model_policy_monitoring_channel(pk):
    # TODO: this should be made in to a real model_policy
    with transaction.atomic():
        mc = MonitoringChannel.objects.select_for_update().filter(pk=pk)
        if not mc:
            return
        mc = mc[0]
        mc.manage_container()


SFLOW_KIND = "sflow"
SFLOW_PORT = 6343
SFLOW_API_PORT = 33333

class SFlowService(Service):
    KIND = SFLOW_KIND

    class Meta:
        app_label = "ceilometer"
        verbose_name = "sFlow Collection Service"
        proxy = True

    default_attributes = {"sflow_port": SFLOW_PORT, "sflow_api_port": SFLOW_API_PORT}

    sync_attributes = ("sflow_port", "sflow_api_port",)

    @property
    def sflow_port(self):
        return self.get_attribute("sflow_port", self.default_attributes["sflow_port"])

    @sflow_port.setter
    def sflow_port(self, value):
        self.set_attribute("sflow_port", value)

    @property
    def sflow_api_port(self):
        return self.get_attribute("sflow_api_port", self.default_attributes["sflow_api_port"])

    @sflow_api_port.setter
    def sflow_api_port(self, value):
        self.set_attribute("sflow_api_port", value)

    def get_instance(self):
        if self.slices.exists():
            slice = self.slices.all()[0]
            if slice.instances.exists():
                return slice.instances.all()[0]

        return None

    @property
    def sflow_api_url(self):
        if not self.get_instance():
            return None
        return "http://" + self.get_instance().get_ssh_ip() + ":" + str(self.sflow_api_port) + "/"

class SFlowTenant(Tenant): 
    class Meta:
        proxy = True

    KIND = SFLOW_KIND

    sync_attributes = ("listening_endpoint", )

    default_attributes = {}
    def __init__(self, *args, **kwargs):
        sflow_services = SFlowService.get_service_objects().all()
        if sflow_services:
            self._meta.get_field("provider_service").default = sflow_services[0].id
        super(SFlowTenant, self).__init__(*args, **kwargs)

    @property
    def creator(self):
        from core.models import User
        if getattr(self, "cached_creator", None):
            return self.cached_creator
        creator_id=self.get_attribute("creator_id")
        if not creator_id:
            return None
        users=User.objects.filter(id=creator_id)
        if not users:
            return None
        user=users[0]
        self.cached_creator = users[0]
        return user

    @creator.setter
    def creator(self, value):
        if value:
            value = value.id
        if (value != self.get_attribute("creator_id", None)):
            self.cached_creator=None
        self.set_attribute("creator_id", value)

    @property
    def listening_endpoint(self):
        return self.get_attribute("listening_endpoint", None)

    @listening_endpoint.setter
    def listening_endpoint(self, value):
        if urlparse(value).scheme != 'udp':
            raise XOSProgrammingError("SFlowTenant: Only UDP listening endpoint URLs are accepted...valid syntax is: udp://ip:port")
        self.set_attribute("listening_endpoint", value)

    def save(self, *args, **kwargs):
        if not self.creator:
            if not getattr(self, "caller", None):
                # caller must be set when creating a SFlow tenant since it creates a slice
                raise XOSProgrammingError("SFlowTenant's self.caller was not set")
            self.creator = self.caller
            if not self.creator:
                raise XOSProgrammingError("SFlowTenant's self.creator was not set")

        if not self.listening_endpoint:
            raise XOSProgrammingError("SFlowTenant's self.listening_endpoint was not set")

        if self.pk is None:
            #Allow only one sflow channel per user and listening_endpoint
            channel_count = sum ( [1 for channel in SFlowTenant.objects.filter(kind=SFLOW_KIND) if ((channel.creator == self.creator) and (channel.listening_endpoint == self.listening_endpoint))] )
            if channel_count > 0:
                raise XOSValidationError("Already %s sflow channels exist for user Can only create max 1 tenant per user and listening endpoint" % str(channel_count))

        super(SFlowTenant, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super(MonitoringChannel, self).delete(*args, **kwargs)

    @property
    def authorized_resource_list(self):
        return ['all']

    @property
    def authorized_resource_list_str(self):
        return ", ".join(self.authorized_resource_list)

