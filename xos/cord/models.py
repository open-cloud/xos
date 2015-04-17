from django.db import models
from core.models import Service, PlCoreBase, Slice, Sliver, Tenant, Node, Image
from core.models.plcorebase import StrippedCharField
import os
from django.db import models
from django.forms.models import model_to_dict
from django.db.models import Q
from operator import itemgetter, attrgetter, methodcaller

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
svc = VOLTService.get_service_objects().all()[0]

t = VOLTTenant(provider_service=svc)
t.caller = User.objects.all()[0]
t.save()

for v in VOLTTenant.objects.all():
    v.caller = User.objects.all()[0]
    v.delete()

for v in VCPETenant.objects.all():
    v.caller = User.objects.all()[0]
    v.delete()
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

    @property
    def vcpe(self):
        vcpe_id=self.get_attribute("vcpe_id")
        if not vcpe_id:
            return None
        vcpes=VCPETenant.objects.filter(id=vcpe_id)
        if not vcpes:
            return None
        return vcpes[0]

    @vcpe.setter
    def vcpe(self, value):
        if value:
            self.set_attribute("vcpe_id", value.id)
        else:
            self.set_attribute("vcpe_id", None)

    def manage_vcpe(self):
        # Each VOLT object owns exactly one VCPE object

        if self.deleted:
            return

        if self.vcpe is None:
            vcpeServices = VCPEService.get_service_objects().all()
            if not vcpeServices:
                raise ConfigurationError("No VCPE Services available")

            vcpe = VCPETenant(provider_service = vcpeServices[0],
                              subscriber_tenant = self)
            vcpe.caller = self.caller
            vcpe.save()

            try:
                self.vcpe = vcpe
                self.save()
            except:
                vcpe.delete()
                raise

    def cleanup_vcpe(self):
        if self.vcpe:
            self.vcpe.delete()
            self.vcpe = None

    def save(self, *args, **kwargs):
        if not getattr(self, "caller", None):
            raise TypeError("VOLTTenant's self.caller was not set")
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

    default_attributes = {"firewall_enable": False,
                          "firewall_rules": "accept all anywhere anywhere",
                          "url_filter_enable": False,
                          "url_filter_rules": "allow all",
                          "cdn_enable": False,
                          "sliver_id": None}

    @property
    def image(self):
        # TODO: logic to pick an image based on the feature set
        #    just use Ubuntu 14.04 for now...
        return Image.objects.get(name="Ubuntu 14.04 LTS")

    @property
    def sliver(self):
        sliver_id=self.get_attribute("sliver_id")
        if not sliver_id:
            return None
        slivers=Sliver.objects.filter(id=sliver_id)
        if not slivers:
            return None
        return slivers[0]

    @sliver.setter
    def sliver(self, value):
        if value:
            self.set_attribute("sliver_id", value.id)
        else:
            self.set_attribute("sliver_id", None)

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
                raise ConfigurationError("The VCPE service has no slicers")

            node =self.pick_node()
            sliver = Sliver(slice = self.provider_service.slices.all()[0],
                            node = node,
                            image = self.image,
                            creator = self.caller,
                            deployment = node.site_deployment.deployment)
            sliver.save()

            try:
                self.sliver = sliver
                self.save()
            except:
                sliver.delete()
                raise

    def cleanup_sliver(self):
        if self.sliver:
            self.sliver.delete()
            self.sliver = None

    def save(self, *args, **kwargs):
        if not getattr(self, "caller", None):
            raise TypeError("VCPETenant's self.caller was not set")
        super(VCPETenant, self).save(*args, **kwargs)
        self.manage_sliver()

    def delete(self, *args, **kwargs):
        self.cleanup_sliver()
        super(VCPETenant, self).delete(*args, **kwargs)

