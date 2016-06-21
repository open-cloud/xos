from django.db import models
from core.models import Service, PlCoreBase, Slice, Instance, Tenant, TenantWithContainer, Node, Image, User, Flavor, Subscriber, NetworkParameter, NetworkParameterType, Port, AddressPool, User
from core.models.plcorebase import StrippedCharField
import os
from django.db import models, transaction
from django.forms.models import model_to_dict
from django.db.models import Q
from operator import itemgetter, attrgetter, methodcaller
from core.models import Tag
from core.models.service import LeastLoadedNodeScheduler
from services.vrouter.models import VRouterService, VRouterTenant
import traceback
from xos.exceptions import *
from xos.config import Config

class ConfigurationError(Exception):
    pass

VOLT_KIND = "vOLT"
CORD_SUBSCRIBER_KIND = "CordSubscriberRoot"

CORD_USE_VTN = getattr(Config(), "networking_use_vtn", False)

# -------------------------------------------
# CordSubscriberRoot
# -------------------------------------------

class CordSubscriberRoot(Subscriber):
    class Meta:
        proxy = True

    KIND = CORD_SUBSCRIBER_KIND

    status_choices = (("enabled", "Enabled"),
                      ("suspended", "Suspended"),
                      ("delinquent", "Delinquent"),
                      ("copyrightviolation", "Copyright Violation"))

    # 'simple_attributes' will be expanded into properties and setters that
    # store the attribute using self.set_attribute / self.get_attribute.

    simple_attributes = ( ("firewall_enable", False),
                          ("firewall_rules", "accept all anywhere anywhere"),
                          ("url_filter_enable", False),
                          ("url_filter_rules", "allow all"),
                          ("url_filter_level", "PG"),
                          ("cdn_enable", False),
                          ("devices", []),
                          ("is_demo_user", False),

                          ("uplink_speed", 1000000000),  # 1 gigabit, a reasonable default?
                          ("downlink_speed", 1000000000),
                          ("enable_uverse", True) )

    default_attributes = {"status": "enabled"}

    sync_attributes = ("firewall_enable",
                       "firewall_rules",
                       "url_filter_enable",
                       "url_filter_rules",
                       "cdn_enable",
                       "uplink_speed",
                       "downlink_speed",
                       "enable_uverse",
                       "status")

    def __init__(self, *args, **kwargs):
        super(CordSubscriberRoot, self).__init__(*args, **kwargs)
        self.cached_volt = None
        self._initial_url_filter_enable = self.url_filter_enable

    @property
    def volt(self):
        volt = self.get_newest_subscribed_tenant(VOLTTenant)
        if not volt:
            return None

        # always return the same object when possible
        if (self.cached_volt) and (self.cached_volt.id == volt.id):
            return self.cached_volt

        #volt.caller = self.creator
        self.cached_volt = volt
        return volt

    @property
    def status(self):
        return self.get_attribute("status", self.default_attributes["status"])

    @status.setter
    def status(self, value):
        if not value in [x[0] for x in self.status_choices]:
            raise Exception("invalid status %s" % value)
        self.set_attribute("status", value)

    def find_device(self, mac):
        for device in self.devices:
            if device["mac"] == mac:
                return device
        return None

    def update_device(self, mac, **kwargs):
        # kwargs may be "level" or "mac"
        #    Setting one of these to None will cause None to be stored in the db
        devices = self.devices
        for device in devices:
            if device["mac"] == mac:
                for arg in kwargs.keys():
                    device[arg] = kwargs[arg]
                self.devices = devices
                return device
        raise ValueError("Device with mac %s not found" % mac)

    def create_device(self, **kwargs):
        if "mac" not in kwargs:
            raise XOSMissingField("The mac field is required")

        if self.find_device(kwargs['mac']):
                raise XOSDuplicateKey("Device with mac %s already exists" % kwargs["mac"])

        device = kwargs.copy()

        devices = self.devices
        devices.append(device)
        self.devices = devices

        return device

    def delete_device(self, mac):
        devices = self.devices
        for device in devices:
            if device["mac"]==mac:
                devices.remove(device)
                self.devices = devices
                return

        raise ValueError("Device with mac %s not found" % mac)

    #--------------------------------------------------------------------------
    # Deprecated -- devices used to be called users

    def find_user(self, uid):
        return self.find_device(uid)

    def update_user(self, uid, **kwargs):
        return self.update_device(uid, **kwargs)

    def create_user(self, **kwargs):
        return self.create_device(**kwargs)

    def delete_user(self, uid):
        return self.delete_user(uid)

    # ------------------------------------------------------------------------

    @property
    def services(self):
        return {"cdn": self.cdn_enable,
                "url_filter": self.url_filter_enable,
                "firewall": self.firewall_enable}

    @services.setter
    def services(self, value):
        pass

    def save(self, *args, **kwargs):
        self.validate_unique_service_specific_id(none_okay=True)
        if (not hasattr(self, 'caller') or not self.caller.is_admin):
            if (self.has_field_changed("service_specific_id")):
                raise XOSPermissionDenied("You do not have permission to change service_specific_id")
        super(CordSubscriberRoot, self).save(*args, **kwargs)
        if (self.volt) and (self.volt.vcpe): # and (self._initial_url_filter_enabled != self.url_filter_enable):
            # 1) trigger manage_bbs_account to run
            # 2) trigger vcpe observer to wake up
            self.volt.vcpe.save()

CordSubscriberRoot.setup_simple_attributes()

# -------------------------------------------
# VOLT
# -------------------------------------------

class VOLTService(Service):
    KIND = VOLT_KIND

    class Meta:
        app_label = "volt"
        verbose_name = "vOLT Service"

class VOLTTenant(Tenant):
    KIND = VOLT_KIND

    class Meta:
        app_label = "volt"
        verbose_name = "vOLT Tenant"

    s_tag = models.IntegerField(null=True, blank=True, help_text="s-tag")
    c_tag = models.IntegerField(null=True, blank=True, help_text="c-tag")

    # at some point, this should probably end up part of Tenant.
    creator = models.ForeignKey(User, related_name='created_volts', blank=True, null=True)

    def __init__(self, *args, **kwargs):
        volt_services = VOLTService.get_service_objects().all()
        if volt_services:
            self._meta.get_field("provider_service").default = volt_services[0].id
        super(VOLTTenant, self).__init__(*args, **kwargs)
        self.cached_vcpe = None

    @property
    def vcpe(self):
        from services.vsg.models import VSGTenant
        vcpe = self.get_newest_subscribed_tenant(VSGTenant)
        if not vcpe:
            return None

        # always return the same object when possible
        if (self.cached_vcpe) and (self.cached_vcpe.id == vcpe.id):
            return self.cached_vcpe

        vcpe.caller = self.creator
        self.cached_vcpe = vcpe
        return vcpe

    @vcpe.setter
    def vcpe(self, value):
        raise XOSConfigurationError("vOLT.vCPE cannot be set this way -- create a new vCPE object and set its subscriber_tenant instead")

    @property
    def subscriber(self):
        if not self.subscriber_root:
            return None
        subs = CordSubscriberRoot.objects.filter(id=self.subscriber_root.id)
        if not subs:
            return None
        return subs[0]

    def manage_vcpe(self):
        # Each VOLT object owns exactly one VCPE object

        if self.deleted:
            return

        if self.vcpe is None:
            from services.vsg.models import VSGService, VSGTenant
            vsgServices = VSGService.get_service_objects().all()
            if not vsgServices:
                raise XOSConfigurationError("No VSG Services available")

            vcpe = VSGTenant(provider_service = vsgServices[0],
                              subscriber_tenant = self)
            vcpe.caller = self.creator
            vcpe.save()

    def manage_subscriber(self):
        if (self.subscriber_root is None):
            # The vOLT is not connected to a Subscriber, so either find an
            # existing subscriber with the same SSID, or autogenerate a new
            # subscriber.
            #
            # TODO: This probably goes away when we rethink the ONOS-to-XOS
            # vOLT API.

            subs = CordSubscriberRoot.get_tenant_objects().filter(service_specific_id = self.service_specific_id)
            if subs:
                sub = subs[0]
            else:
                sub = CordSubscriberRoot(service_specific_id = self.service_specific_id,
                                         name = "autogenerated-for-vOLT-%s" % self.id)
                sub.save()
            self.subscriber_root = sub
            self.save()

    def cleanup_vcpe(self):
        if self.vcpe:
            # print "XXX cleanup vcpe", self.vcpe
            self.vcpe.delete()

    def cleanup_orphans(self):
        from services.vsg.models import VSGTenant
        # ensure vOLT only has one vCPE
        cur_vcpe = self.vcpe
        for vcpe in list(self.get_subscribed_tenants(VSGTenant)):
            if (not cur_vcpe) or (vcpe.id != cur_vcpe.id):
                # print "XXX clean up orphaned vcpe", vcpe
                vcpe.delete()

    def save(self, *args, **kwargs):
        # VOLTTenant probably doesn't need a SSID anymore; that will be handled
        # by CORDSubscriberRoot...
        # self.validate_unique_service_specific_id()

        if (self.subscriber_root is not None):
            subs = self.subscriber_root.get_subscribed_tenants(VOLTTenant)
            if (subs) and (self not in subs):
                raise XOSDuplicateKey("Subscriber should only be linked to one vOLT")

        if not self.creator:
            if not getattr(self, "caller", None):
                # caller must be set when creating a vCPE since it creates a slice
                raise XOSProgrammingError("VOLTTenant's self.caller was not set")
            self.creator = self.caller
            if not self.creator:
                raise XOSProgrammingError("VOLTTenant's self.creator was not set")

        super(VOLTTenant, self).save(*args, **kwargs)
        model_policy_volt(self.pk)

    def delete(self, *args, **kwargs):
        self.cleanup_vcpe()
        super(VOLTTenant, self).delete(*args, **kwargs)

def model_policy_volt(pk):
    # TODO: this should be made in to a real model_policy
    with transaction.atomic():
        volt = VOLTTenant.objects.select_for_update().filter(pk=pk)
        if not volt:
            return
        volt = volt[0]
        volt.manage_vcpe()
        volt.manage_subscriber()
        volt.cleanup_orphans()

class VOLTDevice(PlCoreBase):
    class Meta:
        app_label = "volt"

    name = models.CharField(max_length=254, help_text="name of device", null=False, blank=False)
    volt_service = models.ForeignKey(VOLTService, related_name='volt_devices')
    openflow_id = models.CharField(max_length=254, help_text="OpenFlow ID", null=True, blank=True)
    driver = models.CharField(max_length=254, help_text="driver", null=True, blank=True)
    access_agent = models.ForeignKey("AccessAgent", related_name='volt_devices', blank=True, null=True)

    def __unicode__(self): return u'%s' % (self.name)

class AccessDevice(PlCoreBase):
    class Meta:
        app_label = "volt"

    volt_device = models.ForeignKey(VOLTDevice, related_name='access_devices')
    uplink = models.IntegerField(null=True, blank=True)
    vlan = models.IntegerField(null=True, blank=True)

    def __unicode__(self): return u'%s-%d:%d' % (self.volt_device.name,self.uplink,self.vlan)

class AccessAgent(PlCoreBase):
    class Meta:
        app_label = "volt"

    name = models.CharField(max_length=254, help_text="name of agent", null=False, blank=False)
    volt_service = models.ForeignKey(VOLTService, related_name='access_agents')
    mac = models.CharField(max_length=32, help_text="MAC Address or Access Agent", null=True, blank=True)

    def __unicode__(self): return u'%s' % (self.name)

class AgentPortMapping(PlCoreBase):
    class Meta:
        app_label = "volt"

    access_agent = models.ForeignKey(AccessAgent, related_name='port_mappings')
    mac = models.CharField(max_length=32, help_text="MAC Address", null=True, blank=True)
    port = models.CharField(max_length=32, help_text="Openflow port ID", null=True, blank=True)

    def __unicode__(self): return u'%s-%s-%s' % (self.access_agent.name, self.port, self.mac)



