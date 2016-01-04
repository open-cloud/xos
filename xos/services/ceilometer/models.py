from sets import Set

from core.models import (Service, SitePrivilege, Slice, SlicePrivilege,
                         TenantWithContainer)
from django.db import transaction
from xos.exceptions import XOSProgrammingError, XOSValidationError

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
            self._meta.get_field(
                "provider_service").default = ceilometer_services[0].id
        super(MonitoringChannel, self).__init__(*args, **kwargs)
        self.set_attribute("use_same_instance_for_multiple_tenants", True)

    def can_update(self, user):
        # Allow creation of this model instances for non-admin users also
        return True

    def save(self, *args, **kwargs):
        if not self.creator:
            if not getattr(self, "caller", None):
                # caller must be set when creating a monitoring channel since
                # it creates a slice
                raise XOSProgrammingError(
                    "MonitoringChannel's self.caller was not set")
            self.creator = self.caller
            if not self.creator:
                raise XOSProgrammingError(
                    "MonitoringChannel's self.creator was not set")

        if self.pk is None:
            # Allow only one monitoring channel per user
            channel_count = sum([1 for channel in MonitoringChannel.objects.filter(
                kind=CEILOMETER_KIND) if (channel.creator == self.creator)])
            if channel_count > 0:
                raise XOSValidationError(
                    "Already %s channels exist for user Can only create max 1 MonitoringChannel instance per user" % str(channel_count))

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
            # TODO: Ceilometer publishes the SDN meters without associating to any tenant IDs.
            # For now, ceilometer code is changed to pusblish all such meters with tenant
            # id as "default_admin_tenant". Here add that default tenant as authroized tenant_id
            # for all admin users.
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
        # TODO: Find a better logic to choose unique ceilometer port number for
        # each instance
        if not self.id:
            return None
        return 8888 + self.id

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
