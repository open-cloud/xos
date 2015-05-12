from django.db import models
from core.models import Service, PlCoreBase, Slice, Sliver, Tenant, Node, Image, User
from core.models.plcorebase import StrippedCharField
import os
from django.db import models
from django.forms.models import model_to_dict
from django.db.models import Q
from operator import itemgetter, attrgetter, methodcaller
import traceback
from xos.exceptions import *

"""
import os
import sys
sys.path.append("/opt/xos")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")
import django
from core.models import *
from hpc.models import *
from cord.models import *
django.setup()

t = VOLTTenant()
t.caller = User.objects.all()[0]
t.save()

for v in VOLTTenant.get_tenant_objects().all():
    v.caller = User.objects.all()[0]
    v.delete()

for v in VCPETenant.get_tenant_objects().all():
    v.caller = User.objects.all()[0]
    v.delete()

for v in VOLTTenant.get_tenant_objects().all():
    v.caller = User.objects.all()[0]
    v.delete()

for v in VOLTTenant.get_tenant_objects().all():
    if not v.creator:
        v.creator= User.objects.all()[0]
        v.save()

for v in VCPETenant.get_tenant_objects().all():
    if not v.creator:
        v.creator= User.objects.all()[0]
        v.save()
"""

class ConfigurationError(Exception):
    pass

# -------------------------------------------
# VOLT
# -------------------------------------------

class VOLTService(Service):
    KIND = "vOLT"

    class Meta:
        app_label = "cord"
        verbose_name = "vOLT Service"
        proxy = True

class VOLTTenant(Tenant):
    class Meta:
        proxy = True

    KIND = "vOLT"

    default_attributes = {"vlan_id": None, }

    def __init__(self, *args, **kwargs):
        volt_services = VOLTService.get_service_objects().all()
        if volt_services:
            self._meta.get_field("provider_service").default = volt_services[0].id
        super(VOLTTenant, self).__init__(*args, **kwargs)

    @property
    def vlan_id(self):
        return self.get_attribute("vlan_id", self.default_attributes["vlan_id"])

    @vlan_id.setter
    def vlan_id(self, value):
        self.set_attribute("vlan_id", value)

    @property
    def vcpe(self):
        if getattr(self, "cached_vcpe", None):
            return self.cached_vcpe
        vcpe_id=self.get_attribute("vcpe_id")
        if not vcpe_id:
            return None
        vcpes=VCPETenant.objects.filter(id=vcpe_id)
        if not vcpes:
            return None
        vcpe=vcpes[0]
        vcpe.caller = self.creator
        self.cached_vcpe = vcpe
        return vcpe

    @vcpe.setter
    def vcpe(self, value):
        if value:
            value = value.id
        if (value != self.get_attribute("vcpe_id", None)):
            self.cached_vcpe=None
        self.set_attribute("vcpe_id", value)

    @property
    def creator(self):
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

    def manage_vcpe(self):
        # Each VOLT object owns exactly one VCPE object

        if self.deleted:
            return

        if self.vcpe is None:
            vcpeServices = VCPEService.get_service_objects().all()
            if not vcpeServices:
                raise XOSConfigurationError("No VCPE Services available")

            vcpe = VCPETenant(provider_service = vcpeServices[0],
                              subscriber_tenant = self)
            vcpe.caller = self.creator
            vcpe.save()

            try:
                self.vcpe = vcpe
                super(VOLTTenant, self).save()
            except:
                vcpe.delete()
                raise

    def cleanup_vcpe(self):
        if self.vcpe:
            self.vcpe.delete()
            self.vcpe = None

    def save(self, *args, **kwargs):
        self.validate_unique_service_specific_id()

        if not self.creator:
            if not getattr(self, "caller", None):
                # caller must be set when creating a vCPE since it creates a slice
                raise XOSProgrammingError("VOLTTenant's self.caller was not set")
            self.creator = self.caller
            if not self.creator:
                raise XOSProgrammingError("VOLTTenant's self.creator was not set")

        super(VOLTTenant, self).save(*args, **kwargs)
        self.manage_vcpe()

    def delete(self, *args, **kwargs):
        self.cleanup_vcpe()
        super(VOLTTenant, self).delete(*args, **kwargs)

# -------------------------------------------
# VCPE
# -------------------------------------------

class VCPEService(Service):
    KIND = "vCPE"

    class Meta:
        app_label = "cord"
        verbose_name = "vCPE Service"
        proxy = True

class VCPETenant(Tenant):
    class Meta:
        proxy = True

    KIND = "vCPE"

    sync_attributes = ("firewall_enable",
                       "firewall_rules",
                       "url_filter_enable",
                       "url_filter_rules",
                       "cdn_enable")

    default_attributes = {"firewall_enable": False,
                          "firewall_rules": "accept all anywhere anywhere",
                          "url_filter_enable": False,
                          "url_filter_rules": "allow all",
                          "cdn_enable": False,
                          "sliver_id": None}

    def __init__(self, *args, **kwargs):
        super(VCPETenant, self).__init__(*args, **kwargs)
        self.cached_vbng=None
        self.cached_sliver=None

    @property
    def image(self):
        LOOK_FOR_IMAGES=["Ubuntu 14.04 LTS",    # portal
                         "Ubuntu-14.04-LTS",    # ONOS demo machine
                        ]
        for image_name in LOOK_FOR_IMAGES:
            images = Image.objects.filter(name = image_name)
            if images:
                return images[0]

        raise XOSProgrammingError("No VPCE image (looked for %s)" % str(LOOK_FOR_IMAGES))

    @property
    def sliver(self):
        if getattr(self, "cached_sliver", None):
            return self.cached_sliver
        sliver_id=self.get_attribute("sliver_id")
        if not sliver_id:
            return None
        slivers=Sliver.objects.filter(id=sliver_id)
        if not slivers:
            return None
        sliver=slivers[0]
        sliver.caller = self.creator
        self.cached_sliver = sliver
        return sliver

    @sliver.setter
    def sliver(self, value):
        if value:
            value = value.id
        if (value != self.get_attribute("sliver_id", None)):
            self.cached_sliver=None
        self.set_attribute("sliver_id", value)

    @property
    def creator(self):
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
    def vbng(self):
        if getattr(self, "cached_vbng", None):
            return self.cached_vbng
        vbng_id=self.get_attribute("vbng_id")
        if not vbng_id:
            return None
        vbngs=VBNGTenant.objects.filter(id=vbng_id)
        if not vbngs:
            return None
        vbng=vbngs[0]
        vbng.caller = self.creator
        self.cached_vbng = vbng
        return vbng

    @vbng.setter
    def vbng(self, value):
        if value:
            value = value.id
        if (value != self.get_attribute("vbng_id", None)):
            self.cached_vbng=None
        self.set_attribute("vbng_id", value)

    @property
    def firewall_enable(self):
        return self.get_attribute("firewall_enable", self.default_attributes["firewall_enable"])

    @firewall_enable.setter
    def firewall_enable(self, value):
        self.set_attribute("firewall_enable", value)

    @property
    def firewall_rules(self):
        return self.get_attribute("firewall_rules", self.default_attributes["firewall_rules"])

    @firewall_rules.setter
    def firewall_rules(self, value):
        self.set_attribute("firewall_rules", value)

    @property
    def url_filter_enable(self):
        return self.get_attribute("url_filter_enable", self.default_attributes["url_filter_enable"])

    @url_filter_enable.setter
    def url_filter_enable(self, value):
        self.set_attribute("url_filter_enable", value)

    @property
    def url_filter_rules(self):
        return self.get_attribute("url_filter_rules", self.default_attributes["url_filter_rules"])

    @url_filter_rules.setter
    def url_filter_rules(self, value):
        self.set_attribute("url_filter_rules", value)

    @property
    def cdn_enable(self):
        return self.get_attribute("cdn_enable", self.default_attributes["cdn_enable"])

    @cdn_enable.setter
    def cdn_enable(self, value):
        self.set_attribute("cdn_enable", value)

    def pick_node(self):
        nodes = list(Node.objects.all())
        # TODO: logic to filter nodes by which nodes are up, and which
        #   nodes the slice can instantiate on.
        nodes = sorted(nodes, key=lambda node: node.slivers.all().count())
        return nodes[0]

    def manage_sliver(self):
        # Each VCPE object owns exactly one sliver.

        if self.deleted:
            return

        if (self.sliver is not None) and (self.sliver.image != self.image):
            self.sliver.delete()
            self.sliver = None

        if self.sliver is None:
            if not self.provider_service.slices.count():
                raise XOSConfigurationError("The VCPE service has no slices")

            node =self.pick_node()
            sliver = Sliver(slice = self.provider_service.slices.all()[0],
                            node = node,
                            image = self.image,
                            creator = self.creator,
                            deployment = node.site_deployment.deployment)
            sliver.save()

            try:
                self.sliver = sliver
                super(VCPETenant, self).save()
            except:
                sliver.delete()
                raise

    def cleanup_sliver(self):
        if self.sliver:
            self.sliver.delete()
            self.sliver = None

    def manage_vbng(self):
        # Each vCPE object owns exactly one vBNG object

        if self.deleted:
            return

        if self.vbng is None:
            vbngServices = VBNGService.get_service_objects().all()
            if not vbngServices:
                raise XOSConfigurationError("No VBNG Services available")

            vbng = VBNGTenant(provider_service = vbngServices[0],
                              subscriber_tenant = self)
            vbng.caller = self.creator
            vbng.save()

            try:
                self.vbng = vbng
                super(VCPETenant, self).save()
            except:
                vbng.delete()
                raise

    def cleanup_vbng(self):
        if self.vbng:
            self.vbng.delete()
            self.vbng = None

    def save(self, *args, **kwargs):
        if not self.creator:
            if not getattr(self, "caller", None):
                # caller must be set when creating a vCPE since it creates a slice
                raise XOSProgrammingError("VCPETenant's self.caller was not set")
            self.creator = self.caller
            if not self.creator:
                raise XOSProgrammingError("VCPETenant's self.creator was not set")

        super(VCPETenant, self).save(*args, **kwargs)
        self.manage_sliver()
        self.manage_vbng()

    def delete(self, *args, **kwargs):
        self.cleanup_vbng()
        self.cleanup_sliver()
        super(VCPETenant, self).delete(*args, **kwargs)

#----------------------------------------------------------------------------
# vBNG
#----------------------------------------------------------------------------

class VBNGService(Service):
    KIND = "vBNG"

    class Meta:
        app_label = "cord"
        verbose_name = "vBNG Service"
        proxy = True

class VBNGTenant(Tenant):
    class Meta:
        proxy = True

    KIND = "vBNG"

    default_attributes = {"routeable_subnet": ""}

    @property
    def routeable_subnet(self):
        return self.get_attribute("routeable_subnet", self.default_attributes["routeable_subnet"])

    @routeable_subnet.setter
    def routeable_subnet(self, value):
        self.set_attribute("routeable_subnet", value)
